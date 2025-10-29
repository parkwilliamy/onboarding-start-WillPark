# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import ClockCycles
from cocotb.triggers import Timer, First
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

async def average_frequency(dut):

    freq_sum = 0
    freq_avg_list = [0,0]
    cycles = 0
    time1 = 0
    time2 = 0
    pwm_count = 8
    
    for i in range(8):
        while (cycles < 16700):
        
            await RisingEdge(dut.clk)
            pwm_val_1 = dut.uo_out.value[i]
            await RisingEdge(dut.clk)
            pwm_val_2 = dut.uo_out.value[i]

            pwm_rise = (pwm_val_1 == 0) and (pwm_val_2 == 1)
            if (pwm_rise == 1):
                time1 = cocotb.utils.get_sim_time(units="sec")
                break
            else:
                cycles += 1

        cycles = 0

        while (cycles < 16700):
            await RisingEdge(dut.clk)
            pwm_val_1 = dut.uo_out.value[i]
            await RisingEdge(dut.clk)
            pwm_val_2 = dut.uo_out.value[i]

            pwm_rise = (pwm_val_1 == 0) and (pwm_val_2 == 1)
            if (pwm_rise == 1):
                time2 = cocotb.utils.get_sim_time(units="sec")
                break
            else:
                cycles += 1

        if time2-time1 != 0:
            freq = 1/(time2-time1)
        else:
            freq = 0
            pwm_count -= 1

        freq_sum += freq
        

    if pwm_count != 0:
        freq_avg_list[0] = freq_sum/pwm_count
    else:
        freq_avg_list[0] = 0

    freq_sum = 0
    pwm_count = 8
    time1 = 0
    time2 = 0

    for i in range(8):
        while (cycles < 16700):
        
            await RisingEdge(dut.clk)
            pwm_val_1 = dut.uio_out.value[i]
            await RisingEdge(dut.clk)
            pwm_val_2 = dut.uio_out.value[i]

            pwm_rise = (pwm_val_1 == 0) and (pwm_val_2 == 1)
            if (pwm_rise == 1):
                time1 = cocotb.utils.get_sim_time(units="sec")
                break
            else:
                cycles += 1

        cycles = 0

        while (cycles < 16700):
            await RisingEdge(dut.clk)
            pwm_val_1 = dut.uio_out.value[i]
            await RisingEdge(dut.clk)
            pwm_val_2 = dut.uio_out.value[i]

            pwm_rise = (pwm_val_1 == 0) and (pwm_val_2 == 1)
            if (pwm_rise == 1):
                time2 = cocotb.utils.get_sim_time(units="sec")
                break
            else:
                cycles += 1

        if time2-time1 != 0:
            freq = 1/(time2-time1)
        else:
            freq = 0
            pwm_count -= 1

        freq_sum += freq
        

    if pwm_count != 0:
        freq_avg_list[1] = freq_sum/pwm_count
    else:
        freq_avg_list[1] = 0
    
    return freq_avg_list
    
async def get_duty_cycle(dut):

    duty_cycle_sum_list = [0,0]
    duty_cycle_sum = 0
    cycles = 0
    time1 = 0
    time2 = 0
    pwm_count = 8

    for i in range(8):
        while (cycles < 16700):
        
            await RisingEdge(dut.clk)
            pwm_val_1 = dut.uo_out.value[i]
            await RisingEdge(dut.clk)
            pwm_val_2 = dut.uo_out.value[i]

            pwm_rise = (pwm_val_1 == 0) and (pwm_val_2 == 1)
            if (pwm_rise == 1):
                time1 = cocotb.utils.get_sim_time(units="sec")
                break
            else:
                cycles += 1

        cycles = 0

        while (cycles < 16700):
            await RisingEdge(dut.clk)
            pwm_val_1 = dut.uo_out.value[i]
            await RisingEdge(dut.clk)
            pwm_val_2 = dut.uo_out.value[i]

            pwm_fall = (pwm_val_1 == 1) and (pwm_val_2 == 0)
            if (pwm_fall == 1):
                time2 = cocotb.utils.get_sim_time(units="sec")
                break
            else:
                cycles += 1

        if time2-time1 == 0:
            if pwm_val_2 == Logic(1):
                duty_cycle = 1
            else:
                duty_cycle = 0
        else:
            duty_cycle = (time2-time1)/0.00033289 

        if duty_cycle == 0:
            pwm_count -= 1

        duty_cycle_sum += duty_cycle

    if pwm_count != 0:
        duty_cycle_sum_list[0] = duty_cycle_sum*100/pwm_count
    else:
        duty_cycle_sum_list[0] = 0

    duty_cycle_sum = 0

    for i in range(8):
        while (cycles < 16700):
        
            await RisingEdge(dut.clk)
            pwm_val_1 = dut.uio_out.value[i]
            await RisingEdge(dut.clk)
            pwm_val_2 = dut.uio_out.value[i]

            pwm_rise = (pwm_val_1 == 1) and (pwm_val_2 == 0)
            if (pwm_rise == 1):
                time1 = cocotb.utils.get_sim_time(units="sec")
                break
            else:
                cycles += 1

        cycles = 0

        while (cycles < 16700):
            await RisingEdge(dut.clk)
            pwm_val_1 = dut.uio_out.value[i]
            await RisingEdge(dut.clk)
            pwm_val_2 = dut.uio_out.value[i]

            pwm_fall = (pwm_val_1 == 0) and (pwm_val_2 == 1)
            if (pwm_fall == 1):
                time2 = cocotb.utils.get_sim_time(units="sec")
                break
            else:
                cycles += 1

        
        if time2-time1 == 0:
            if pwm_val_2 == Logic(1):
                duty_cycle = 1
            else:
                duty_cycle = 0
        else:
            duty_cycle = (time2-time1)/0.00033289 

        duty_cycle_sum += duty_cycle

    if pwm_count != 0:
        duty_cycle_sum_list[1] = duty_cycle_sum*100/pwm_count
    else:
        duty_cycle_sum_list[1] = 0

    return duty_cycle_sum_list
    



'''
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
    ui_in_val = await send_spi_transaction(dut, 1, 0x00, 0xF0)  # Write transaction
    assert dut.uo_out.value == 0xF0, f"Expected 0xF0, got {dut.uo_out.value}"
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
    '''
    dut._log.info("All Outputs Enabled with PWM")

    ui_in_val = await send_spi_transaction(dut, 1, 0x00, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x01, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x02, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x03, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0xF0)
    await ClockCycles(dut.clk, 100)

    freq_avg_list = await average_frequency(dut)

    assert freq_avg_list[0] >= 2970 and freq_avg_list[0] <= 3030, f"Expected 2970 <= freq_uo_avg <= 3030, got {freq_avg_list[0]}"
    assert freq_avg_list[1] >= 2970 and freq_avg_list[1] <= 3030, f"Expected 2970 <= freq_uo_avg <= 3030, got {freq_avg_list[1]}"
   
    await ClockCycles(dut.clk, 1000) 

    dut._log.info("All Outputs Disabled")

    ui_in_val = await send_spi_transaction(dut, 1, 0x00, 0x00)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x01, 0x00)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x02, 0x00)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x03, 0x00)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0x00)
    await ClockCycles(dut.clk, 100)

    freq_avg_list = await average_frequency(dut)

    assert freq_avg_list[0] == 0, f"Expected freq_uo_avg = 0, got {freq_avg_list[0]}"
    assert freq_avg_list[1] == 0, f"Expected freq_uio_avg = 0, got {freq_avg_list[1]}"
   
    await ClockCycles(dut.clk, 1000) 
    '''

    dut._log.info("Some Outputs Enabled with PWM")

    ui_in_val = await send_spi_transaction(dut, 1, 0x00, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x01, 0x00)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x02, 0xF0)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x03, 0x00)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0xC0)
    await ClockCycles(dut.clk, 100)

    freq_avg_list = await average_frequency(dut)

    assert freq_avg_list[0] >= 2970 and freq_avg_list[0] <= 3030, f"Expected 2970 <= freq_uo_avg <= 3030, got {freq_avg_list[0]}"
    assert freq_avg_list[1] == 0, f"Expected 2970 <= freq_uo_avg <= 3030, got {freq_avg_list[1]}"
   
    await ClockCycles(dut.clk, 1000) 
    
    dut._log.info("PWM Frequency test completed successfully")
    
'''
@cocotb.test()
async def test_pwm_duty(dut):
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
    dut._log.info("100% Duty Cycle")

    ui_in_val = await send_spi_transaction(dut, 1, 0x00, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x01, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x02, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x03, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0xFF)
    await ClockCycles(dut.clk, 100)

    duty_cycle_list = await get_duty_cycle(dut)

    assert duty_cycle_list[0] == 100, f"Expected 100% duty cycle, got {duty_cycle_list[0]}"
    assert duty_cycle_list[1] == 100, f"Expected 100% duty cycle, got {duty_cycle_list[1]}"
   
    await ClockCycles(dut.clk, 1000) 

    dut._log.info("0% Duty Cycle")

    ui_in_val = await send_spi_transaction(dut, 1, 0x00, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x01, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x02, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x03, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0x00)
    await ClockCycles(dut.clk, 100)

    duty_cycle_list = await get_duty_cycle(dut)

    assert duty_cycle_list[0] == 0, f"Expected 0% duty cycle, got {duty_cycle_list[0]}"
    assert duty_cycle_list[1] == 0, f"Expected 0% duty cycle, got {duty_cycle_list[1]}"
   
    await ClockCycles(dut.clk, 1000) 

    dut._log.info("50% Duty Cycle")

    ui_in_val = await send_spi_transaction(dut, 1, 0x00, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x01, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x02, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x03, 0xFF)
    await ClockCycles(dut.clk, 100)
    
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0x80)
    await ClockCycles(dut.clk, 100)

    duty_cycle_list = await get_duty_cycle(dut)

    assert duty_cycle_list[0] >= 49 and duty_cycle_list[0] <= 51, f"Expected 50% duty cycle, got {duty_cycle_list[0]}"
    assert duty_cycle_list[1] >= 49 and duty_cycle_list[1] <= 51, f"Expected 50% duty cycle, got {duty_cycle_list[1]}"
   
    await ClockCycles(dut.clk, 1000) 
    
    dut._log.info("PWM Duty Cycle test completed successfully")
   '''