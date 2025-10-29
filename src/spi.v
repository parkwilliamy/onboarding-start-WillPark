/*
 * Copyright (c) 2024 Will Park
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module spi (
    input wire rst_n, clk, SCLK, COPI, nCS,
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

  assign data0 = inter0;
  assign data1 = inter1;
  assign data2 = inter2;
  assign data3 = inter3;
  assign data4 = inter4;

  wire SCLK_rise, nCS_rise;
  assign SCLK_rise = SCLK_shift[1] && !SCLK_shift[2];
  assign nCS_rise = nCS_shift[1] && !nCS_shift[2];

  //CDC Registers

  reg [2:0] SCLK_shift, nCS_shift, COPI_shift;

  always @ (posedge clk or negedge rst_n) begin

    if (!rst_n) begin

      current_state <= IDLE;
      inter0 <= 0;
      inter1 <= 0;
      inter2 <= 0;
      inter3 <= 0;
      inter4 <= 0;

      SCLK_shift <= 0;
      nCS_shift <= 0;
      COPI_shift <= 0;

    end else begin

      SCLK_shift <= {SCLK_shift[1:0], SCLK};

      COPI_shift <= {COPI_shift[2], COPI_shift[0], COPI};

      nCS_shift <= {nCS_shift[1:0], nCS};

      if (SCLK_rise) begin // if SCLK has + edge
      
          COPI_shift <= {COPI_shift[1:0], COPI};
          current_state <= next_state;

      end

      else if (nCS_rise) begin // if nCS has + edge

          case (addr)

          0: inter0 <= data;
          1: inter1 <= data;
          2: inter2 <= data;
          3: inter3 <= data;
          4: inter4 <= data;

          endcase

      end

    end

  end

  always @ (*) begin

    case (current_state) 

      IDLE: begin

        if (!nCS_shift[2]) next_state = WRITE;
        else next_state = IDLE;
        
      end

      WRITE: begin

        if (!nCS_shift[2] && COPI_shift[2]) next_state = ADDRESS1;
        else next_state = IDLE; //ignore reads 

      end

      ADDRESS1: begin

        if (!nCS_shift[2]) next_state = ADDRESS2;
        else next_state = IDLE;

      end

      ADDRESS2: begin

        if (!nCS_shift[2]) next_state = ADDRESS3;
        else next_state = IDLE;

      end

      ADDRESS3: begin

        if (!nCS_shift[2]) next_state = ADDRESS4;
        else next_state = IDLE;

      end

      ADDRESS4: begin

        if (!nCS_shift[2]) next_state = ADDRESS5;
        else next_state = IDLE;

      end

      ADDRESS5: begin

        if (!nCS_shift[2]) next_state = ADDRESS6;
        else next_state = IDLE;

      end

      ADDRESS6: begin

        if (!nCS_shift[2]) next_state = ADDRESS7;
        else next_state = IDLE;

      end

      ADDRESS7: begin

        if (!nCS_shift[2]) begin
            if (addr <= MAX_ADDR) next_state = DATA1;
            else next_state = IDLE;
        end

        else next_state = IDLE;

      end

      DATA1: begin

        if (!nCS_shift[2]) next_state = DATA2;
        else next_state = IDLE;

      end

      DATA2: begin

        if (!nCS_shift[2]) next_state = DATA3;
        else next_state = IDLE;

      end

      DATA3: begin

        if (!nCS_shift[2]) next_state = DATA4;
        else next_state = IDLE;

      end

      DATA4: begin

        if (!nCS_shift[2]) next_state = DATA5;
        else next_state = IDLE;

      end

      DATA5: begin

        if (!nCS_shift[2]) next_state = DATA6;
        else next_state = IDLE;

      end

      DATA6: begin

        if (!nCS_shift[2]) next_state = DATA7;
        else next_state = IDLE;

      end

      DATA7: begin

        if (!nCS_shift[2]) next_state = DATA8;
        else next_state = IDLE;

      end

      DATA8: begin

        next_state = WRITE;

      end

    endcase

  end

  always @ (*) begin

    case (current_state) 

      ADDRESS1: begin

        if (!nCS_shift[2]) addr[6] = COPI_shift[2];

      end

      ADDRESS2: begin

        if (!nCS_shift[2]) addr[5] = COPI_shift[2];
        
      end

      ADDRESS3: begin

        if (!nCS_shift[2]) addr[4] = COPI_shift[2];
       

      end

      ADDRESS4: begin

        if (!nCS_shift[2]) addr[3] = COPI_shift[2];
        

      end

      ADDRESS5: begin

        if (!nCS_shift[2]) addr[2] = COPI_shift[2];
        

      end

      ADDRESS6: begin

        if (!nCS_shift[2]) addr[1] = COPI_shift[2];


      end

      ADDRESS7: begin

        if (!nCS_shift[2]) addr[0] = COPI_shift[2];
          
      end

      DATA1: begin

        if (!nCS_shift[2]) data[7] = COPI_shift[2];

      end

      DATA2: begin

        if (!nCS_shift[2]) data[6] = COPI_shift[2];

      end

      DATA3: begin

        if (!nCS_shift[2]) data[5] = COPI_shift[2];
        
      end

      DATA4: begin

        if (!nCS_shift[2]) data[4] = COPI_shift[2];
   
      end

      DATA5: begin

        if (!nCS_shift[2]) data[3] = COPI_shift[2];

      end

      DATA6: begin

        if (!nCS_shift[2]) data[2] = COPI_shift[2];

      end

      DATA7: begin

        if (!nCS_shift[2]) data[1] = COPI_shift[2];
      
      end

      DATA8: begin

        if (!nCS_shift[2]) data[0] = COPI_shift[2];
        
      end

  

    endcase

  end

endmodule