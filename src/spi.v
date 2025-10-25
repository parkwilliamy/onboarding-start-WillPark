/*
 * Copyright (c) 2024 Will Park
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module spi (
    input wire rst_n, SCLK, COPI, nCS,
    output [7:0] data0, data1, data2, data3, data4
);

  reg [1:0] current_state, next_state;
  localparam IDLE = 0, WRITE = 1, ADDRESS = 2, DATA = 3;

  reg [6:0] addr;
  reg [2:0] addr_index;
  localparam MAX_ADDR = 4;

  reg [7:0] data;
  reg [2:0] data_index;
  reg [7:0] inter0, inter1, inter2, inter3, inter4;

  assign data0 = inter0;
  assign data1 = inter1;
  assign data2 = inter2;
  assign data3 = inter3;
  assign data4 = inter4;

  // CDC Registers
  reg COPI_2;

  always @ (posedge SCLK or posedge nCS or negedge rst_n) begin

    if (!rst_n) begin

        current_state <= IDLE;
        inter0 <= 0;
        inter1 <= 0;
        inter2 <= 0;
        inter3 <= 0;
        inter4 <= 0;

    end

    else begin
    
        if (nCS) begin

            case (addr)

                0: inter0 <= data;
                1: inter1 <= data;
                2: inter2 <= data;
                3: inter3 <= data;
                4: inter4 <= data;

            endcase

        end

        else begin

            COPI_2 <= COPI;
            current_state <= next_state;

        end

    end

  end

  always @ (negedge SCLK) begin

    if (current_state == WRITE) begin

        addr_index <= 7;
        data_index <= 7;

    end

    if (current_state == ADDRESS && addr_index > 0) begin

        addr_index <= addr_index - 1;

    end

    if (current_state == DATA && data_index > 0) begin

        data_index <= data_index - 1; //shift data out on -edge

    end

  end

  always @ (*) begin

    case (current_state) 

      IDLE: begin

        if (!nCS) next_state = WRITE;

      end

      WRITE: begin

        if (COPI_2) begin
          next_state = ADDRESS;
        end
        else next_state = IDLE; //ignore reads 

      end

      ADDRESS: begin

        addr[addr_index-1] = COPI_2;
        if (addr_index > 0) next_state = ADDRESS;    
        else begin
          if (addr <= MAX_ADDR) next_state = DATA; 
          else next_state = IDLE; //reject invalid addresses
        end

      end

      DATA: begin

        data[data_index] = COPI_2;
        if (data_index > 0) next_state = DATA;
        else next_state = IDLE;

      end

  

    endcase

  end

endmodule