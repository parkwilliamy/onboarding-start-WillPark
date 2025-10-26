/*
 * Copyright (c) 2024 Will Park
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module spi (
    input wire rst_n, SCLK, COPI, nCS,
    output [7:0] data0, data1, data2, data3, data4
);

  reg [4:0] current_state, next_state;
  localparam IDLE = 0, 
            WRITE = 1, 
            ADDRESS1 = 2, 
            ADDRESS2 = 3,
            ADDRESS3 = 4,
            ADDRESS4 = 5,
            ADDRESS5 = 6,
            ADDRESS6 = 7,
            ADDRESS7 = 8,
            DATA1 = 9,
            DATA2 = 10,
            DATA3 = 11,
            DATA4 = 12,
            DATA5 = 13,
            DATA6 = 14,
            DATA7 = 15,
            DATA8 = 16;

  reg [6:0] addr;
  localparam MAX_ADDR = 4;

  reg [7:0] data;
  reg [7:0] inter0, inter1, inter2, inter3, inter4;

  reg transaction_finished;

  assign data0 = inter0;
  assign data1 = inter1;
  assign data2 = inter2;
  assign data3 = inter3;
  assign data4 = inter4;

  // CDC Registers
  reg COPI_2;

  always @ (posedge SCLK or negedge rst_n) begin

    if (!rst_n) begin

        current_state <= IDLE;

    end

    else begin
    
        COPI_2 <= COPI;
        current_state <= next_state;

    end

  end

  always @ (posedge nCS) begin

    case (addr)

        0: inter0 <= data;
        1: inter1 <= data;
        2: inter2 <= data;
        3: inter3 <= data;
        4: inter4 <= data;

    endcase

  end

  always @ (*) begin

    case (current_state) 

      IDLE: begin

        if (!nCS) next_state = WRITE;
        else next_state = IDLE;

      end

      WRITE: begin

        if (COPI_2) begin
          next_state = ADDRESS1;
        end
        else next_state = IDLE; //ignore reads 

      end

      ADDRESS1: begin

        if (!nCS) begin
            addr[6] = COPI_2;
            next_state = ADDRESS2;
        end

        else next_state = IDLE;

      end

      ADDRESS2: begin

        if (!nCS) begin
            addr[5] = COPI_2;
            next_state = ADDRESS3;
        end

        else next_state = IDLE;

      end

      ADDRESS3: begin

        if (!nCS) begin
            addr[4] = COPI_2;
            next_state = ADDRESS4;
        end

        else next_state = IDLE;

      end

      ADDRESS4: begin

        if (!nCS) begin
            addr[3] = COPI_2;
            next_state = ADDRESS5;
        end

        else next_state = IDLE;

      end

      ADDRESS5: begin

        if (!nCS) begin
            addr[2] = COPI_2;
            next_state = ADDRESS6;
        end

        else next_state = IDLE;

      end

      ADDRESS6: begin

        if (!nCS) begin
            addr[1] = COPI_2;
            next_state = ADDRESS7;
        end

        else next_state = IDLE;

      end

      ADDRESS7: begin

        if (!nCS) begin
            addr[0] = COPI_2;
            if (addr <= MAX_ADDR) next_state = DATA1;
            else next_state = IDLE;
        end

        else next_state = IDLE;

      end

      DATA1: begin

        if (!nCS) begin
            data[7] = COPI_2;
            next_state = DATA2;
        end

        else next_state = IDLE;

      end

      DATA2: begin

        if (!nCS) begin
            data[6] = COPI_2;
            next_state = DATA3;
        end

        else next_state = IDLE;

      end

      DATA3: begin

        if (!nCS) begin
            data[5] = COPI_2;
            next_state = DATA4;
        end

        else next_state = IDLE;

      end

      DATA4: begin

        if (!nCS) begin
            data[4] = COPI_2;
            next_state = DATA5;
        end

        else next_state = IDLE;

      end

      DATA5: begin

        if (!nCS) begin
            data[3] = COPI_2;
            next_state = DATA6;
        end

        else next_state = IDLE;

      end

      DATA6: begin

        if (!nCS) begin
            data[2] = COPI_2;
            next_state = DATA7;
        end

        else next_state = IDLE;

      end

      DATA7: begin

        if (!nCS) begin
            data[1] = COPI_2;
            next_state = DATA8;
        end

        else next_state = IDLE;

      end

      DATA8: begin

        if (!nCS) begin
            data[0] = COPI_2;
        end

        next_state = IDLE;

      end

  

    endcase

  end

endmodule