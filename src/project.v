/*
 * Copyright (c) 2024 Will Park
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_uwasic_onboarding_WillPark (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  wire [7:0] en_reg_out_7_0;
  wire [7:0] en_reg_out_15_8;
  wire [7:0] en_reg_pwm_7_0;
  wire [7:0] en_reg_pwm_15_8;
  wire [7:0] pwm_duty_cycle;

  assign en_reg_out_7_0 = rst_n ? addr0 : 0;
  assign en_reg_out_15_8 = rst_n ? addr1 : 0;
  assign en_reg_pwm_7_0 = rst_n ? addr2 : 0;
  assign en_reg_pwm_15_8 = rst_n ? addr3 : 0;
  assign pwm_duty_cycle = rst_n ? addr4 : 0;

  reg [7:0] addr0, addr1, addr2, addr3, addr4;
  
  // All output pins must be assigned. If not used, assign to 0.
  assign uo_out  = ui_in + uio_in;  // Example: ou_out is the sum of ui_in and uio_in
  assign uio_out = 0;
  assign uio_oe = 8'hFF; // Set all IOs to output

  // Instantiate the PWM module
  pwm_peripheral pwm_peripheral_inst (
    .clk(clk),
    .rst_n(rst_n),
    .en_reg_out_7_0(en_reg_out_7_0),
    .en_reg_out_15_8(en_reg_out_15_8),
    .en_reg_pwm_7_0(en_reg_pwm_7_0),
    .en_reg_pwm_15_8(en_reg_pwm_15_8),
    .pwm_duty_cycle(pwm_duty_cycle),
    .out({uio_out, uo_out})
  );

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, clk, rst_n, ui_in[7:3], uio_in, 1'b0};
  
  wire SCLK, COPI, nCS;
  assign SCLK = ui_in[0];
  assign COPI = ui_in[1];
  assign nCS = ui_in[2];

  // CDC Registers
  reg COPI_1;

  spi spi_inst (
    .rst_n(rst_n),
    .SCLK(SCLK),
    .COPI(COPI_1),
    .nCS(nCS),
    .addr0(addr0),
    .addr1(addr1),
    .addr2(addr2),
    .addr3(addr3),
    .addr4(addr4)
  );

  always @ (posedge clk) begin

    COPI_1 <= COPI;

  end

endmodule