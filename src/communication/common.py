def twos_complement(hex_str, bits):
    value = int(hex_str, 16)
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value


def to_hex(val, nbits):
    return hex((val + (1 << nbits)) % (1 << nbits))[2:].zfill(8)


class Communication:
    connected: bool = False
    timeout: bool = False
    read_all: bytes

    def connect(self):
        pass

    def disconnect(self):
        pass

    @staticmethod
    def parse_sending_joystick_movement(pan_speed: int,
                                        tilt_speed: int,
                                        pan_dir: int,
                                        tilt_dir: int,
                                        pan_on: int,
                                        tilt_on: int) -> str:
        """
        0- 0x7A
        1- 0x02
        2- 0x00
        3- 0x00
        4- 0x00
        5- 0x00
        6- Pan Speed (Low Byte)
        7- Pan Speed (High Byte)
        8- Tilt Speed (Low Byte)
        9- Tilt Speed(High Byte)
        10-
                                  Bit0=0
                     Bit1=Pan_Dir: Right=0 Left=1
                     Bit2=Tilt_Dir: up=0 down=1
                     Bit3=Pan_on/off: off=0 on=1
                                   Bit4=Tilt_on/off: off=0 on=1
                                   Bit5=0
                                   Bit6=0
                     Bit7=0
                11-0x00
                12-0x00
                13-Checksum
                14-0xA7

        returning hex string
        """
        byte_0 = '7a'
        byte_1 = '02'
        byte_2 = '00'
        byte_3 = '00'
        byte_4 = '00'
        byte_5 = '00'
        pan_speed_hex = "{0:#0{1}x}".format(pan_speed, 6)[2:]
        byte_pan_speed_high = pan_speed_hex[:2]
        byte_pan_speed_low = pan_speed_hex[2:]
        tilt_speed_hex = "{0:#0{1}x}".format(tilt_speed, 6)[2:]
        byte_tilt_speed_high = tilt_speed_hex[:2]
        byte_tilt_speed_low = tilt_speed_hex[2:]
        byte_10_bits = str(0) + str(0) + str(0) + str(tilt_on) + str(pan_on) + str(tilt_dir) + str(pan_dir) + str(0)
        bytes_10_hex = "{0:0>2X}".format(int(byte_10_bits, 2))
        byte_11 = '00'
        byte_12 = '00'
        data = [byte_0, byte_1, byte_2, byte_3, byte_4, byte_5, byte_pan_speed_low, byte_pan_speed_high,
                byte_tilt_speed_low,
                byte_tilt_speed_high, bytes_10_hex, byte_11, byte_12]
        packet = [chr(int(x, 16)) for x in data]
        checksum = 0
        for el in packet:
            checksum ^= ord(el)
        str_checksum = str(hex(checksum)[2:])
        if len(str_checksum) == 1:
            str_checksum = '0' + str_checksum
        byte_14 = 'a7'
        print([byte_0, byte_1, byte_2, byte_3, byte_4, byte_5, byte_pan_speed_low, byte_pan_speed_high,
               byte_tilt_speed_low,
               byte_tilt_speed_high, bytes_10_hex, byte_11, byte_12, checksum, byte_14])
        return ''.join(
            [byte_0, byte_1, byte_2, byte_3, byte_4, byte_5, byte_pan_speed_low, byte_pan_speed_high,
             byte_tilt_speed_low,
             byte_tilt_speed_high, bytes_10_hex, byte_11, byte_12, str_checksum, byte_14])

    @staticmethod
    def parse_sending_goto_position(pan_degree: int,
                                    tilt_degree: int,
                                    pan_speed: int,
                                    tilt_speed: int,
                                    pan_goto_position_on: int,
                                    tilt_goto_position_on: int,
                                    pan_dir: int,
                                    tilt_dir: int) -> str:
        """
        0- 0x7A
        1- 0x01
        2- Pan Degree (Low Byte)
        3- Pan Degree (High Byte)
        4- Tilt Degree(Low Byte)
        5- Tilt Degree(High Byte)
        6- Pan Speed (Low Byte) (DEGREE/S)
        7- Pan Speed ((High Byte)
        8- Tilt Speed (Low Byte) (DEGREE/S)
        9- Tilt Speed(High Byte)
        10-
          Bit0=1
          Bit1=0
          Bit2=0
          Bit3=Pan_GOTO POSATION:  off=0 on=1
          Bit4=Tilt_GOTO POSATION:    off=0 on=1
          Bit5= Sign_ Pan: neg=0 pos=1
                                     Bit6= Sign_ Tilt:  neg=0 pos=1
          Bit7=0
        11-0x00
        12-0x00
        13-Checksum
        14-0xA7

        returning hex string
        """
        byte_0 = '7a'
        byte_1 = '01'
        pan_degree_hex = "{0:#0{1}x}".format(pan_degree, 6)[2:]
        byte_pan_degree_high = pan_degree_hex[:2]
        byte_pan_degree_low = pan_degree_hex[2:]
        tilt_degree_hex = "{0:#0{1}x}".format(tilt_degree, 6)[2:]
        byte_tilt_degree_high = tilt_degree_hex[:2]
        byte_tilt_degree_low = tilt_degree_hex[2:]
        pan_speed_hex = "{0:#0{1}x}".format(pan_speed, 6)[2:]
        byte_pan_speed_high = pan_speed_hex[:2]
        byte_pan_speed_low = pan_speed_hex[2:]
        tilt_speed_hex = "{0:#0{1}x}".format(tilt_speed, 6)[2:]
        byte_tilt_speed_high = tilt_speed_hex[:2]
        byte_tilt_speed_low = tilt_speed_hex[2:]
        print(tilt_dir, pan_dir, tilt_goto_position_on, pan_goto_position_on)
        byte_10_bits = str(0) + str(tilt_dir) + str(pan_dir) + str(tilt_goto_position_on) + str(
            pan_goto_position_on) + str(0) + str(0) + str(1)
        # byte_10_bits = str(1) + str(0) + str(0) + str(pan_goto_position_on) + str(tilt_goto_position_on) + str(
        #     pan_dir) + str(tilt_dir) + str(0)
        bytes_10_hex = "{0:0>2X}".format(int(byte_10_bits, 2))
        byte_11 = '00'
        byte_12 = '00'
        data = [byte_0, byte_1, byte_pan_degree_low, byte_pan_degree_high, byte_tilt_degree_low, byte_tilt_degree_high,
                byte_pan_speed_low, byte_pan_speed_high, byte_tilt_speed_low,
                byte_tilt_speed_high, bytes_10_hex, byte_11, byte_12]
        print('DATA is:', data)
        packet = [chr(int(x, 16)) for x in data]
        checksum = 0
        for el in packet:
            checksum ^= ord(el)
        str_checksum = str(hex(checksum)[2:])
        if len(str_checksum) == 1:
            str_checksum = '0' + str_checksum

        byte_14 = 'a7'
        print([byte_0, byte_1, byte_pan_degree_low, byte_pan_degree_high, byte_tilt_degree_low, byte_tilt_degree_high,
               byte_pan_speed_low, byte_pan_speed_high, byte_tilt_speed_low,
               byte_tilt_speed_high, bytes_10_hex, byte_11, byte_12, str_checksum, byte_14])
        return ''.join(
            [byte_0, byte_1, byte_pan_degree_low, byte_pan_degree_high, byte_tilt_degree_low, byte_tilt_degree_high,
             byte_pan_speed_low, byte_pan_speed_high, byte_tilt_speed_low,
             byte_tilt_speed_high, bytes_10_hex, byte_11, byte_12, str_checksum, byte_14])

    @staticmethod
    def parse_sending_zero_encoder(pan_zero: int,
                                   tilt_zero: int) -> str:
        """
        0- 0x7A
        1- 0x03
        2- 0x00
        3- 0x00
        4- 0x00
        5- 0x00
        6- 0x00
        7- 0x00
        8- 0x00
        9- 0x00
        10-
          Bit0=0
             Bit1=0
             Bit2=0
             Bit3=Pan_zero:  non-zero=0 zero=1
                           Bit4=Tilt_zero: non-zero=0 zero=1
                           Bit5=0
                           Bit6=0
              Bit7=0
        11-0x00
        12-0x00
        13-Checksum
        14-0xA7

        returning hex string
        """
        byte_0 = '7a'
        byte_1 = '03'
        byte_2 = '00'
        byte_3 = '00'
        byte_4 = '00'
        byte_5 = '00'
        byte_6 = '00'
        byte_7 = '00'
        byte_8 = '00'
        byte_9 = '00'
        byte_10_bits = str(0) + str(0) + str(0) + str(tilt_zero) + str(pan_zero) + str(0) + str(0) + str(0)
        bytes_10_hex = "{0:0>2X}".format(int(byte_10_bits, 2))
        byte_11 = '00'
        byte_12 = '00'
        data = [byte_0, byte_1, byte_2, byte_3, byte_4, byte_5, byte_6, byte_7, byte_8,
                byte_9, bytes_10_hex, byte_11, byte_12]
        print('DATA is:', data)
        packet = [chr(int(x, 16)) for x in data]
        checksum = 0
        for el in packet:
            checksum ^= ord(el)
        str_checksum = str(hex(checksum)[2:])
        if len(str_checksum) == 1:
            str_checksum = '0' + str_checksum

        byte_14 = 'a7'
        print([byte_0, byte_1, byte_2, byte_3, byte_4, byte_5, byte_6, byte_7, byte_8,
               byte_9, bytes_10_hex, byte_11, byte_12, str_checksum, byte_14])
        return ''.join(
            [byte_0, byte_1, byte_2, byte_3, byte_4, byte_5, byte_6, byte_7, byte_8,
             byte_9, bytes_10_hex, byte_11, byte_12, str_checksum, byte_14])

    @staticmethod
    def parse_sending_assign_limitation(pan_degree_right: int,
                                        pan_degree_left: int,
                                        tilt_degree_up: int,
                                        tilt_degree_down: int,
                                        pan_limit_on: int,
                                        tilt_limit_on: int,
                                        pan_dir_right: int,
                                        pan_dir_left: int,
                                        tilt_dir_up: int,
                                        tilt_dir_down: int) -> str:
        """
        0- 0x7A
        1- 0x04
        2- Pan Degree Right (Low Byte)
        3- Pan Degree Right (High Byte)
        4- Pan Degree Left (Low Byte)
        5- Pan Degree Left (High Byte)
        6- Tilt Degree Up(Low Byte)
        7- Tilt Degree Up(High Byte)
        8- Tilt Degree Down(Low Byte)
        9- Tilt Degree Down (High Byte)
        10-
              Bit0=0
                 Bit1= Pan_LIMIT:  non-LIMIT=0 LIMIT=1
                 Bit2= Tilt_LIMIT: non-LIMIT=0 LIMIT=1
                 Bit3= Sign_Pan Right:  neg=0 pos=1
                               Bit4= Sign_Pan Left:    neg=0 pos=1
                               Bit5= Sign_Tilt Up:       neg=0 pos=1
                               Bit6= Sign_Tilt Down:  neg=0 pos=1
                  Bit7=0
        11-0x00
        12-0x00
        13-Checksum

        returning hex string
        """
        byte_0 = '7a'
        byte_1 = '04'
        pan_degree_right_hex = "{0:#0{1}x}".format(pan_degree_right, 6)[2:]
        byte_pan_degree_right_high = pan_degree_right_hex[:2]
        byte_pan_degree_right_low = pan_degree_right_hex[2:]
        pan_degree_left_hex = "{0:#0{1}x}".format(pan_degree_left, 6)[2:]
        byte_pan_degree_left_high = pan_degree_left_hex[:2]
        byte_pan_degree_left_low = pan_degree_left_hex[2:]
        tilt_degree_up_hex = "{0:#0{1}x}".format(tilt_degree_up, 6)[2:]
        byte_tilt_degree_up_high = tilt_degree_up_hex[:2]
        byte_tilt_degree_up_low = tilt_degree_up_hex[2:]
        tilt_degree_down_hex = "{0:#0{1}x}".format(tilt_degree_down, 6)[2:]
        byte_tilt_degree_down_high = tilt_degree_down_hex[:2]
        byte_tilt_degree_down_low = tilt_degree_down_hex[2:]
        byte_10_bits = str(0) + str(tilt_dir_down) + str(tilt_dir_up) + str(pan_dir_left) + str(pan_dir_right) + str(
            tilt_limit_on) + str(pan_limit_on) + str(0)
        # byte_10_bits = str(1) + str(0) + str(0) + str(pan_goto_position_on) + str(tilt_goto_position_on) + str(
        #     pan_dir) + str(tilt_dir) + str(0)
        bytes_10_hex = "{0:0>2X}".format(int(byte_10_bits, 2))
        byte_11 = '00'
        byte_12 = '00'
        data = [byte_0, byte_1, byte_pan_degree_right_low, byte_pan_degree_right_high, byte_pan_degree_left_low,
                byte_pan_degree_left_high,
                byte_tilt_degree_up_low, byte_tilt_degree_up_high, byte_tilt_degree_down_low,
                byte_tilt_degree_down_high, bytes_10_hex, byte_11, byte_12]
        print('DATA is:', data)
        packet = [chr(int(x, 16)) for x in data]
        checksum = 0
        for el in packet:
            checksum ^= ord(el)
        str_checksum = str(hex(checksum)[2:])
        if len(str_checksum) == 1:
            str_checksum = '0' + str_checksum

        byte_14 = 'a7'
        print([byte_0, byte_1, byte_pan_degree_right_low, byte_pan_degree_right_high, byte_pan_degree_left_low,
               byte_pan_degree_left_high,
               byte_tilt_degree_up_low, byte_tilt_degree_up_high, byte_tilt_degree_down_low,
               byte_tilt_degree_down_high, bytes_10_hex, byte_11, byte_12, str_checksum, byte_14])
        return ''.join(
            [byte_0, byte_1, byte_pan_degree_right_low, byte_pan_degree_right_high, byte_pan_degree_left_low,
             byte_pan_degree_left_high,
             byte_tilt_degree_up_low, byte_tilt_degree_up_high, byte_tilt_degree_down_low,
             byte_tilt_degree_down_high, bytes_10_hex, byte_11, byte_12, str_checksum, byte_14])

    @staticmethod
    def parse_sending_goto_reference(pan_reference: int,
                                     tilt_reference: int) -> str:
        """
        0- 0x7A
        1- 0x05
        2- 0x00
        3- 0x00
        4- 0x00
        5- 0x00
        6- 0x00
        7- 0x00
        8- 0x00
        9- 0x00
        10-
              Bit0=0
                     Bit1=0
                     Bit2=0
                     Bit3=0
                                   Bit4=0
                                   Bit5=0
                                   Bit6=Pan_REFRENCE:  non-REFRENCE=0 REFRENCE=1
                      Bit7=Tilt_REFRENCE:   non-REFRENCE=0 REFRENCE=1
        11-0x00
        12-0x00
        13-Checksum
        14-0xA7

        returning hex string
        """
        byte_0 = '7a'
        byte_1 = '05'
        byte_2 = '00'
        byte_3 = '00'
        byte_4 = '00'
        byte_5 = '00'
        byte_6 = '00'
        byte_7 = '00'
        byte_8 = '00'
        byte_9 = '00'
        byte_10_bits = str(tilt_reference) + str(pan_reference) + str(0) + str(0) + str(0) + str(0) + str(0) + str(0)
        bytes_10_hex = "{0:0>2X}".format(int(byte_10_bits, 2))
        byte_11 = '00'
        byte_12 = '00'
        data = [byte_0, byte_1, byte_2, byte_3, byte_4, byte_5, byte_6, byte_7, byte_8,
                byte_9, bytes_10_hex, byte_11, byte_12]
        print('DATA is:', data)
        packet = [chr(int(x, 16)) for x in data]
        checksum = 0
        for el in packet:
            checksum ^= ord(el)
        str_checksum = str(hex(checksum)[2:])
        if len(str_checksum) == 1:
            str_checksum = '0' + str_checksum

        byte_14 = 'a7'
        print([byte_0, byte_1, byte_2, byte_3, byte_4, byte_5, byte_6, byte_7, byte_8,
               byte_9, bytes_10_hex, byte_11, byte_12, str_checksum, byte_14])
        return ''.join(
            [byte_0, byte_1, byte_2, byte_3, byte_4, byte_5, byte_6, byte_7, byte_8,
             byte_9, bytes_10_hex, byte_11, byte_12, str_checksum, byte_14])

    @staticmethod
    def parse_sending_scan_mode(pan_degree_right: int,
                                pan_degree_left: int,
                                tilt_degree_up: int,
                                tilt_degree_down: int,
                                pan_scan_on: int,
                                tilt_scan_on: int,
                                pan_dir_right: int,
                                pan_dir_left: int,
                                tilt_dir_up: int,
                                tilt_dir_down: int,
                                scan_speed: int) -> str:
        """
        0- x7A
        1- 0x06
        2- Pan Degree Right (Low Byte)
        3- Pan Degree Right (High Byte)
        4- Pan Degree Left (Low Byte)
        5- Pan Degree Left (High Byte)
        6- Tilt Degree Up(Low Byte)
        7- Tilt Degree Up(High Byte)
        8- Tilt Degree Down(Low Byte)
        9- Tilt Degree Down (High Byte)
        10-
              Bit0=0
                     Bit1= Pan_ SCAN:  off=0 on=1
                     Bit2= Tilt_ SCAN: off=0 on=1
                     Bit3= Sign_Pan Right:  neg=0 pos=1
                                   Bit4= Sign_Pan Left:    neg=0 pos=1
                                   Bit5= Sign_Tilt Up:       neg=0 pos=1
                                   Bit6= Sign_Tilt Down:  neg=0 pos=1
                      Bit7=0
        11-Pan/Tilt Speed (Low Byte)
        12-Pan/Tilt Speed(High Byte)
        13-Checksum
        14-0xA7

        returning hex string
        """
        byte_0 = '7a'
        byte_1 = '06'
        pan_degree_right_hex = "{0:#0{1}x}".format(pan_degree_right, 6)[2:]
        byte_pan_degree_right_high = pan_degree_right_hex[:2]
        byte_pan_degree_right_low = pan_degree_right_hex[2:]
        pan_degree_left_hex = "{0:#0{1}x}".format(pan_degree_left, 6)[2:]
        byte_pan_degree_left_high = pan_degree_left_hex[:2]
        byte_pan_degree_left_low = pan_degree_left_hex[2:]
        tilt_degree_up_hex = "{0:#0{1}x}".format(tilt_degree_up, 6)[2:]
        byte_tilt_degree_up_high = tilt_degree_up_hex[:2]
        byte_tilt_degree_up_low = tilt_degree_up_hex[2:]
        tilt_degree_down_hex = "{0:#0{1}x}".format(tilt_degree_down, 6)[2:]
        byte_tilt_degree_down_high = tilt_degree_down_hex[:2]
        byte_tilt_degree_down_low = tilt_degree_down_hex[2:]
        byte_10_bits = str(0) + str(tilt_dir_down) + str(tilt_dir_up) + str(pan_dir_left) + str(pan_dir_right) + str(
            tilt_scan_on) + str(pan_scan_on) + str(0)
        bytes_10_hex = "{0:0>2X}".format(int(byte_10_bits, 2))
        scan_speed_hex = "{0:#0{1}x}".format(scan_speed, 6)[2:]
        byte_scan_speed_high = scan_speed_hex[:2]
        byte_scan_speed_low = scan_speed_hex[2:]
        data = [byte_0, byte_1, byte_pan_degree_right_low, byte_pan_degree_right_high, byte_pan_degree_left_low,
                byte_pan_degree_left_high,
                byte_tilt_degree_up_low, byte_tilt_degree_up_high, byte_tilt_degree_down_low,
                byte_tilt_degree_down_high, bytes_10_hex, byte_scan_speed_low, byte_scan_speed_high]
        print('DATA is:', data)
        packet = [chr(int(x, 16)) for x in data]
        checksum = 0
        for el in packet:
            checksum ^= ord(el)
        str_checksum = str(hex(checksum)[2:])
        if len(str_checksum) == 1:
            str_checksum = '0' + str_checksum

        byte_14 = 'a7'
        print([byte_0, byte_1, byte_pan_degree_right_low, byte_pan_degree_right_high, byte_pan_degree_left_low,
               byte_pan_degree_left_high,
               byte_tilt_degree_up_low, byte_tilt_degree_up_high, byte_tilt_degree_down_low,
               byte_tilt_degree_down_high, bytes_10_hex, byte_scan_speed_low, byte_scan_speed_high, str_checksum,
               byte_14])
        return ''.join(
            [byte_0, byte_1, byte_pan_degree_right_low, byte_pan_degree_right_high, byte_pan_degree_left_low,
             byte_pan_degree_left_high,
             byte_tilt_degree_up_low, byte_tilt_degree_up_high, byte_tilt_degree_down_low,
             byte_tilt_degree_down_high, bytes_10_hex, byte_scan_speed_low, byte_scan_speed_high, str_checksum,
             byte_14])

    @staticmethod
    def parse_sending_numbers(number: int,
                              which_number: int,
                              sign_number: int) -> str:
        """
        0- x7A
        1- 0x55
        2- Number (Low Low Byte)
        3- Number (Low Byte)
        4- Number (Mid Byte)
        5- Number (High Byte)
        6- Which Number
        7-
               Bit0= 0
              Bit1= 0
              Bit2= 0
              Bit3= Sign_Number:  neg=0 pos=1
                                  Bit4=0
                                  Bit5= 0
                                  Bit6= 0
              Bit7=0
        8-0
        9-0
        10-0
        11-0
        12-0
        13-Checksum
        14-0xA7

        returning hex string
        """
        byte_0 = '7a'
        byte_1 = '55'
        number_hex = to_hex(number, 32)
        byte_number_high = number_hex[:2]
        byte_number_mid = number_hex[2:4]
        byte_number_low = number_hex[4:6]
        byte_number_low_low = number_hex[6:]
        byte_which_number = str(0) + str(which_number)  # which number is range 0 to 9
        byte_7_bits = str(0) + str(0) + str(0) + str(0) + str(sign_number) + str(0) + str(0) + str(0)
        bytes_7_hex = "{0:0>2X}".format(int(byte_7_bits, 2))
        byte_8 = "00"
        byte_9 = "00"
        byte_10 = "00"
        byte_11 = "00"
        byte_12 = "00"
        data = [byte_0, byte_1, byte_number_low_low, byte_number_low, byte_number_mid,
                byte_number_high,
                byte_which_number, bytes_7_hex, byte_8,
                byte_9, byte_10, byte_11, byte_12]
        print('DATA is:', data)
        packet = [chr(int(x, 16)) for x in data]
        checksum = 0
        for el in packet:
            checksum ^= ord(el)
        str_checksum = str(hex(checksum)[2:])
        if len(str_checksum) == 1:
            str_checksum = '0' + str_checksum

        byte_14 = 'a7'
        print([byte_0, byte_1, byte_number_low_low, byte_number_low, byte_number_mid,
               byte_number_high,
               byte_which_number, bytes_7_hex, byte_8,
               byte_9, byte_10, byte_11, byte_12, str_checksum, byte_14])
        return ''.join(
            [byte_0, byte_1, byte_number_low_low, byte_number_low, byte_number_mid,
             byte_number_high,
             byte_which_number, bytes_7_hex, byte_8,
             byte_9, byte_10, byte_11, byte_12, str_checksum, byte_14])

    @staticmethod
    def parse_reading(data: list) -> dict:
        """ 0- 0x7A
            1- Pan_ Degree  (Low Byte)
            2- Pan_ Degree (Mid Byte)
            3- Pan_ Degree (High Byte)
            4- Tilt_ Degree  (Low Byte)
            5- Tilt_ Degree (Mid Byte)
            6- Tilt_ Degree (High Byte)
            7- Pan_Speed(Low Byte)
            8- Pan_Speed(High Byte)
            9- Tilt_Speed(Low Byte)
            10- Tilt_Speed(High Byte)
            11- Pan_Motor_Current
            12- Tilt_Motor_Current
            13-
              Bit0=1
              Bit1=Pan Position  Not Reached =0   Reached =1
              Bit2= Tilt Position  Not Reached =0   Reached =1
              Bit3=0
              Bit4=0
              Bit5= Sign_ Pan: neg=0 pos=1
                                         Bit6= Sign_ Tilt:  neg=0 pos=1
              Bit7=0
            14-  (Pan Motor)
              Bit0=Over voltage:                                  OFF=0 ON=1
              Bit1=Under voltage:                                OFF=0 ON=1
              Bit2=Motor Enable/Disable:                  OFF=0 ON=1
              Bit3=Positive limit switch condition:    OFF=0 ON=1
              Bit4=Negative limit switch condition:  OFF=0 ON=1
              Bit5=Tracking:                                           OFF=0 ON=1
              Bit6=0
              Bit7=0
            15-  (Tilt Motor)
              Bit0=Over voltage:                                   OFF=0 ON=1
              Bit1=Under voltage:                                 OFF=0 ON=1
              Bit2=Motor Enable/Disable:                   OFF=0 ON=1
              Bit3=Up limit switch condition:              OFF=0 ON=1
              Bit4=Down  limit switch condition:        OFF=0 ON=1
              Bit5=Tracking:                                            OFF=0 ON=1
                                         Bit6=0
              Bit7=0
            16-0x00
            17-0x00
            18- 0x00
            19-checksum """

        byte_0 = data[0]
        pan_degree_low_byte = data[1]
        pan_degree_mid_byte = data[2]
        pan_degree_high_byte = data[3]
        tilt_degree_low_byte = data[4]
        tilt_degree_mid_byte = data[5]
        tilt_degree_high_byte = data[6]
        pan_speed_low_byte = data[7]
        pan_speed_high_byte = data[8]
        tilt_speed_low_byte = data[9]
        tilt_speed_high_byte = data[10]
        pan_motor_current = data[11]
        tilt_motor_current = data[12]
        byte_13_bits_string = "{0:08b}".format(int(data[13], 16))[::-1]
        byte_13_bit_0 = bool(int(byte_13_bits_string[0]))
        pan_position_reached = bool(int(byte_13_bits_string[1]))
        tilt_position_reached = bool(int(byte_13_bits_string[2]))
        byte_13_bit_3 = bool(int(byte_13_bits_string[3]))
        byte_13_bit_4 = bool(int(byte_13_bits_string[4]))
        sign_pan = bool(int(byte_13_bits_string[5]))
        sign_tilt = bool(int(byte_13_bits_string[6]))
        byte_13_bit_7 = bool(int(byte_13_bits_string[7]))
        byte_pan_motor = "{0:08b}".format(int(data[14], 16))[::-1]
        pan_over_voltage = bool(int(byte_pan_motor[0]))
        pan_under_voltage = bool(int(byte_pan_motor[1]))
        pan_motor_enable_disable = bool(int(byte_pan_motor[2]))
        pan_positive_limit_switch = bool(int(byte_pan_motor[3]))
        pan_negative_limit_switch = bool(int(byte_pan_motor[4]))
        pan_tracking = bool(int(byte_pan_motor[5]))
        byte_14_bit_6 = bool(int(byte_pan_motor[6]))
        byte_14_bit_7 = bool(int(byte_pan_motor[7]))
        byte_tilt_motor = "{0:08b}".format(int(data[15], 16))[::-1]
        tilt_over_voltage = bool(int(byte_tilt_motor[0]))
        tilt_under_voltage = bool(int(byte_tilt_motor[1]))
        tilt_motor_enable_disable = bool(int(byte_tilt_motor[2]))
        tilt_up_limit_switch = bool(int(byte_tilt_motor[3]))
        tilt_down_limit_switch = bool(int(byte_tilt_motor[4]))
        tilt_tracking = bool(int(byte_tilt_motor[5]))
        byte_15_bit_6 = bool(int(byte_tilt_motor[6]))
        byte_15_bit_7 = bool(int(byte_tilt_motor[7]))
        byte_16 = data[16]
        byte_17 = data[17]
        byte_18 = data[18]
        packet = [chr(int(x, 16)) for x in data[:19]]
        checksum = 0
        for el in packet:
            checksum ^= ord(el)
        str_checksum = str(hex(checksum)[2:])
        byte_20 = data[19]
        dict_ret: dict = {
            'panDegree': twos_complement(pan_degree_high_byte + pan_degree_mid_byte + pan_degree_low_byte, 16),
            'tiltDegree': twos_complement(tilt_degree_high_byte + tilt_degree_mid_byte + tilt_degree_low_byte, 16),
            'panSpeed': int(pan_speed_high_byte + pan_speed_low_byte, 16),
            'tiltSpeed': int(tilt_speed_high_byte + tilt_speed_low_byte, 16),
            'panMotorCurrent': int(pan_motor_current, 16),
            'tiltMotorCurrent': int(tilt_motor_current, 16),
            'panPositionReached': pan_position_reached,
            'tiltPositionReached': tilt_position_reached,
            'signPan': sign_pan,
            'signTilt': sign_tilt,
            'panOverVoltage': pan_over_voltage,
            'panUnderVoltage': pan_under_voltage,
            'tiltOverVoltage': tilt_over_voltage,
            'tiltUnderVoltage': tilt_under_voltage,
            'panMotorEnable': pan_motor_enable_disable,
            'panPositiveLimitSwitch': pan_positive_limit_switch,
            'panNegativeLimitSwitch': pan_negative_limit_switch,
            'panTracking': pan_tracking,
            'tiltMotorEnable': tilt_motor_enable_disable,
            'tiltUpLimitSwitch': tilt_up_limit_switch,
            'tiltDownLimitSwitch': tilt_down_limit_switch,
            'tiltTracking': tilt_tracking
        }
        return dict_ret
