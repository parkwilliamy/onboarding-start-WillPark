# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import ClockCycles
#from cocotb.triggers import ValueChange
from cocotb.types import Logic
from cocotb.types import LogicArray

async def await_half_sclk(dut):
    """Wait for the SCLK signal to go high or low."""
    start_time = cocotb.utils.get_sim_time(units="ns")
    while True:
        await ClockCycles(dut.clk, 1)
        # Wait for half of the SCLK period (10 us)
        if (start_time + 100*100*0.5) < cocotb.utils.get_sim_time(units="ns"):
            break
    return

def ui_in_logicarray(ncs, bit, sclk):
    """Setup the ui_in value as a LogicArray."""
    return LogicArray(f"00000{ncs}{bit}{sclk}")

async def send_spi_transaction(dut, r_w, address, data):
    """
    Send an SPI transaction with format:
    - 1 bit for Read/Write
    - 7 bits for address
    - 8 bits for data
    
    Parameters:
    - r_w: boolean, True for write, False for read
    - address: int, 7-bit address (0-127)
    - data: LogicArray or int, 8-bit data
    """
    # Convert data to int if it's a LogicArray
    if isinstance(data, LogicArray):
        data_int = int(data)
    else:
        data_int = data
    # Validate inputs
    if address < 0 or address > 127:
        raise ValueError("Address must be 7-bit (0-127)")
    if data_int < 0 or data_int > 255:
        raise ValueError("Data must be 8-bit (0-255)")
    # Combine RW and address into first byte
    first_byte = (int(r_w) << 7) | address
    # Start transaction - pull CS low
    sclk = 0
    ncs = 0
    bit = 0
    # Set initial state with CS low
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    await ClockCycles(dut.clk, 1)
    # Send first byte (RW + Address)
    for i in range(8):
        bit = (first_byte >> (7-i)) & 0x1
        # SCLK low, set COPI
        sclk = 0
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
        # SCLK high, keep COPI
        sclk = 1
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
    # Send second byte (Data)
    for i in range(8):
        bit = (data_int >> (7-i)) & 0x1
        # SCLK low, set COPI
        sclk = 0
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
        # SCLK high, keep COPI
        sclk = 1
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
    # End transaction - return CS high
    sclk = 0
    ncs = 1
    bit = 0
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    await ClockCycles(dut.clk, 600)
    return ui_in_logicarray(ncs, bit, sclk)

@cocotb.test()
async def test_spi(dut):
    dut._log.info("Start SPI test")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    ncs = 1
    bit = 0
    sclk = 0
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    dut._log.info("Test project behavior")
    dut._log.info("Write transaction, address 0x00, data 0xF0")
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0x01)  # Write transaction
    assert dut.uo_out.value == 0x01, f"Expected 0x01, got {dut.uo_out.value}"
    await ClockCycles(dut.clk, 1000) 

    dut._log.info("Write transaction, address 0x01, data 0xCC")
    ui_in_val = await send_spi_transaction(dut, 1, 0x01, 0xCC)  # Write transaction
    assert dut.uio_out.value == 0xCC, f"Expected 0xCC, got {dut.uio_out.value}"
    await ClockCycles(dut.clk, 100)

    dut._log.info("Write transaction, address 0x30 (invalid), data 0xAA")
    ui_in_val = await send_spi_transaction(dut, 1, 0x30, 0xAA)
    await ClockCycles(dut.clk, 100)

    dut._log.info("Read transaction (invalid), address 0x00, data 0xBE")
    ui_in_val = await send_spi_transaction(dut, 0, 0x30, 0xBE)
    assert dut.uo_out.value == 0xF0, f"Expected 0xF0, got {dut.uo_out.value}"
    await ClockCycles(dut.clk, 100)
    
    dut._log.info("Read transaction (invalid), address 0x41 (invalid), data 0xEF")
    ui_in_val = await send_spi_transaction(dut, 0, 0x41, 0xEF)
    await ClockCycles(dut.clk, 100)

    dut._log.info("Write transaction, address 0x02, data 0xFF")
    ui_in_val = await send_spi_transaction(dut, 1, 0x02, 0xFF)  # Write transaction
    await ClockCycles(dut.clk, 100)

    dut._log.info("Write transaction, address 0x04, data 0xCF")
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0xCF)  # Write transaction
    await ClockCycles(dut.clk, 30000)

    dut._log.info("Write transaction, address 0x04, data 0xFF")
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0xFF)  # Write transaction
    await ClockCycles(dut.clk, 30000)

    dut._log.info("Write transaction, address 0x04, data 0x00")
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0x00)  # Write transaction
    await ClockCycles(dut.clk, 30000)

    dut._log.info("Write transaction, address 0x04, data 0x01")
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0x01)  # Write transaction
    await ClockCycles(dut.clk, 30000)

    dut._log.info("SPI test completed successfully")

'''
@cocotb.test()
async def test_pwm_freq(dut):
    # Write your test here
    dut._log.info("Start PWM frequency test")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    ncs = 1
    bit = 0
    sclk = 0
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    dut._log.info("Test project behavior")
    dut._log.info("All Outputs Enabled with PWM, en_reg_out_7_0 = 0xFF, en_reg_out_15_8 = 0xFF, en_reg_pwm_7_0 = 0xFF, en_reg_pwm_15_8 = 0xFF, pwm_duty_cycle = 0xF0")

    ui_in_val = await send_spi_transaction(dut, 1, 0x00, 0x01)
    await ClockCycles(dut.clk, 30000)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x01, 0xFF)
    await ClockCycles(dut.clk, 30000)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x02, 0x01)
    await ClockCycles(dut.clk, 30000)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x03, 0xFF)
    await ClockCycles(dut.clk, 30000)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0xF0)
    await ClockCycles(dut.clk, 30000)
    
    freq_uo_out_sum = 0
    time1 = 0 
    time2 = 0
    
    await ValueChange(dut.uo_out)

    if LogicArray(dut.uo_out.value)[0] == Logic(1):
            time1 = cocotb.utils.get_sim_time(units="sec")
            await ValueChange(dut.uo_out)
            if LogicArray(dut.uo_out.value)[0] == Logic(1):
                time2 = cocotb.utils.get_sim_time(units="sec")
                freq_uo_out = 1 / (time2 - time1)
                freq_uo_out_sum += freq_uo_out

    elif LogicArray(dut.uo_out.value)[0] == Logic(0):
            time1 = cocotb.utils.get_sim_time(units="sec")
            await ValueChange(dut.uo_out)
            if LogicArray(dut.uo_out.value)[0] == Logic(0):
                time2 = cocotb.utils.get_sim_time(units="sec")
                freq_uo_out = 1 / (time2 - time1)
                freq_uo_out_sum += freq_uo_out
    
    
    for i in range(8):
        # Wait for a change in the packed signal
        await ValueChange(dut.uo_out)

        # Check the specific bit
        if LogicArray(dut.uo_out.value)[i] == Logic(1):
            time1 = cocotb.utils.get_sim_time(units="s")
            await ValueChange(dut.uo_out)
            if LogicArray(dut.uo_out.value)[i] == Logic(1):
                time2 = cocotb.utils.get_sim_time(units="s")
                freq_uo_out = 1 / (time2 - time1)
                freq_uo_out_sum += freq_uo_out

                 # Repeat for uio_out
        await ValueChange(dut.uio_out)
        if LogicArray(dut.uio_out.value)[i] == Logic(1):
            time1 = cocotb.utils.get_sim_time(units="s")
            await ValueChange(dut.uio_out)
            if LogicArray(dut.uio_out.value)[i] == Logic(1):
                time2 = cocotb.utils.get_sim_time(units="s")
                freq_uio_out = 1 / (time2 - time1)
                freq_uio_out_sum += freq_uio_out
    
    freq_uo_out_avg = freq_uo_out_sum
    #freq_uio_out_avg = freq_uio_out_sum/8
    assert time2-time1 > 0, f"Expected nonzero time difference, got {time1-time2}"
    assert freq_uo_out_avg >= 2970 and freq_uo_out_avg <= 3030, f"Expected 2970-3030Hz, got {freq_uo_out_avg}"
   
    #assert freq_uio_out_avg >= 2970 and freq_uio_out_avg <= 3030, f"Expected 2970-3030Hz, got {freq_uio_out_avg}"
    await ClockCycles(dut.clk, 1000) 
    
    dut._log.info("PWM Frequency test completed successfully")
    '''

@cocotb.test()
async def test_pwm_duty(dut):
    # Write your test here
    dut._log.info("PWM Duty Cycle test completed successfully")
