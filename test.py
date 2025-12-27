import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb_test.simulator import run
from cocotb_coverage.coverage import CoverPoint, CoverCross, coverage_db


def pack_lanes(l0: int, l1: int, l2: int, l3: int) -> int:
    return (l0 << (3 * 128)) | (l1 << (2 * 128)) | (l2 << 128) | l3

def unpack_lanes(word: int):
    mask = (1 << 128) - 1
    l3 = word & mask
    l2 = (word >> 128) & mask
    l1 = (word >> (2 * 128)) & mask
    l0 = (word >> (3 * 128)) & mask
    return l0, l1, l2, l3

def rotate_lanes_right(lanes):
    """
    Circular rotation (as in the PDF figures):
        [lane_0, lane_1, lane_2, lane_3] ->
        [lane_3, lane_0, lane_1, lane_2]
    """
    l0, l1, l2, l3 = lanes
    return [l3, l0, l1, l2]
@CoverPoint(
    "func.shift_index",
    xf=lambda shift: shift,
    bins=[0, 1, 2, 3]
)
def cover_shift_index(shift):
    pass


@CoverPoint(
    "func.cycle_count",
    xf=lambda cycle: cycle,
    bins=[0, 1, 2, 3, 4, 5]
)
def cover_cycle(cycle):
    pass


@cocotb.test()
async def test_data_shifting_and_pins(dut):

    clock = Clock(dut.clk, 2, unit="step")
    cocotb.start_soon(clock.start())

    # ---------------- Reset ----------------
    dut.rst.value = 1
    dut.input_pin.value = 0
    dut.lane_0.value = 0
    dut.lane_1.value = 0
    dut.lane_2.value = 0
    dut.lane_3.value = 0

    for _ in range(3):
        await RisingEdge(dut.clk)

    dut.rst.value = 0
    dut._log.info("Reset deasserted")
    await RisingEdge(dut.clk)

    # ---------------- Test Data ----------------
    lane_0 = int("000102030405060708090A0B0C0D0E0F", 16)
    lane_1 = int("101112131415161718191A1B1C1D1E1F", 16)
    lane_2 = int("202122232425262728292A2B2C2D2E2F", 16)
    lane_3 = int("303132333435363738393A3B3C3D3E3F", 16)

    lanes = [lane_0, lane_1, lane_2, lane_3]

    NUM_CYCLES = 6
    prev_output_pin = None

    # ---------------- Coverage bins ----------------
    hit_shift_bins = set()
    hit_cycle_bins = set()

    ALL_SHIFT_BINS = {0, 1, 2, 3}
    ALL_CYCLE_BINS = {0, 1, 2, 3, 4, 5}

    # ---------------- Main Loop ----------------
    for cycle in range(NUM_CYCLES):

        shift_index = cycle % 4

        # ---- Functional Coverage Sampling ----
        cover_shift_index(shift_index)
        cover_cycle(cycle)
        hit_shift_bins.add(shift_index)
        hit_cycle_bins.add(cycle)

        dut._log.info(f"======== CYCLE {cycle} ========")

        dut.lane_0.value = lanes[0]
        dut.lane_1.value = lanes[1]
        dut.lane_2.value = lanes[2]
        dut.lane_3.value = lanes[3]

        packed = pack_lanes(*lanes)
        dut.input_pin.value = packed

        dut._log.info(
            "Input lanes:\n"
            f"  lane_0 = 0x{lanes[0]:032x}\n"
            f"  lane_1 = 0x{lanes[1]:032x}\n"
            f"  lane_2 = 0x{lanes[2]:032x}\n"
            f"  lane_3 = 0x{lanes[3]:032x}\n"
            f"  input_pin = 0x{packed:0128x}"
        )

        await RisingEdge(dut.clk)
        await Timer(1, unit="step")

        out_word = int(dut.output_pin.value)
        out_l0, out_l1, out_l2, out_l3 = unpack_lanes(out_word)

        dut._log.info(
            "Output lanes (from output_pin):\n"
            f"  lane_0_out = 0x{out_l0:032x}\n"
            f"  lane_1_out = 0x{out_l1:032x}\n"
            f"  lane_2_out = 0x{out_l2:032x}\n"
            f"  lane_3_out = 0x{out_l3:032x}\n"
            f"  output_pin = 0x{out_word:0128x}"
        )

        if prev_output_pin is None:
            prev_output_pin = out_word
        else:
            assert out_word == prev_output_pin, (
                "output_pin changed between cycles – expected constant value"
            )

        assert out_l0 == out_l1 == out_l2 == out_l3, (
            "Split lanes are not identical"
        )

        lanes = rotate_lanes_right(lanes)

    # ---------------- Coverage Calculation ----------------
    total_bins = len(ALL_SHIFT_BINS) + len(ALL_CYCLE_BINS)
    hit_bins = len(hit_shift_bins) + len(hit_cycle_bins)
    coverage_percent = (hit_bins / total_bins) * 100 if total_bins else 0

    dut._log.info(f"Functional Coverage = {coverage_percent:.2f}%")

    # ---------------- Export Coverage ----------------
    coverage_db.export_to_yaml("functional_coverage.yml")

    dut._log.info("Task 2 data shifting + pin driving test PASSED!")



def run_sim():
    """Run cocotb test using cocotb-test wrapper (no Makefile needed)."""
    run(
        verilog_sources=["dut.v"],
        toplevel="dut",             
        module="test",                
        sim="icarus",                                   
        waves=True                                       
    )


if __name__ == "__main__":
    run_sim()
