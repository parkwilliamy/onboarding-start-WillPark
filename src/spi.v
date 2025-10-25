/*
 * Copyright (c) 2024 Will Park
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module spi (
    input wire rst_n, SCLK, COPI, nCS,
    output reg [7:0] addr0, addr1, addr2, addr3, addr4
);

  reg [1:0] current_state, next_state;
  localparam IDLE = 0, WRITE = 1, ADDRESS = 2, DATA = 3;

  reg [6:0] addr;
  reg [2:0] addr_index;
  localparam MAX_ADDR = 4;

  reg [7:0] data;
  reg [2:0] data_index;

  // CDC Registers
  reg COPI_2;

  always @ (posedge SCLK) begin

    COPI_2 <= COPI;
    current_state <= next_state;

  end

  always @ (negedge rst_n) begin

    current_state <= IDLE;
    addr0 <= 0;
    addr1 <= 0;
    addr2 <= 0;
    addr3 <= 0;
    addr4 <= 0;

  end

  always @ (posedge nCS) begin

    case (addr)

        0: addr0 <= data;
        1: addr1 <= data;
        2: addr2 <= data;
        3: addr3 <= data;
        4: addr4 <= data;

    endcase

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