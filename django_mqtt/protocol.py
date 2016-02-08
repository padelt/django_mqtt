import paho.mqtt.client as mqtt
import struct


MQTTTypes = [
    0,
    mqtt.CONNECT,
    mqtt.CONNACK,
    mqtt.PUBLISH,
    mqtt.PUBACK,
    mqtt.PUBREC,
    mqtt.PUBREL,
    mqtt.PUBCOMP,
    mqtt.SUBSCRIBE,
    mqtt.SUBACK,
    mqtt.UNSUBSCRIBE,
    mqtt.UNSUBACK,
    mqtt.PINGREQ,
    mqtt.PINGRESP,
    mqtt.DISCONNECT,
    15
]

MQTT_QoS0 = int('00', 2)
MQTT_QoS1 = int('01', 2)
MQTT_QoS2 = int('10', 2)

MQTTQoS = [MQTT_QoS0, MQTT_QoS1, MQTT_QoS2, int('11', 2)]

MQTTFlagsDUP = int('1000', 2)
MQTTFlagsQoS = int('0110', 2)
MQTTFlagsRETAIN = int('0001', 2)

MQTTFlagsTable = {
    mqtt.CONNECT: int('0000', 2),
    mqtt.CONNACK: int('0000', 2),
    mqtt.PUBLISH: None,
    mqtt.PUBACK: int('0000', 2),
    mqtt.PUBREC: int('0000', 2),
    mqtt.PUBREL: int('0010', 2),
    mqtt.PUBCOMP: int('0000', 2),
    mqtt.SUBSCRIBE: int('0010', 2),
    mqtt.SUBACK: int('0000', 2),
    mqtt.UNSUBSCRIBE: int('0010', 2),
    mqtt.UNSUBACK: int('0000', 2),
    mqtt.PINGREQ: int('0000', 2),
    mqtt.PINGRESP: int('0000', 2),
    mqtt.DISCONNECT: int('0000', 2)
}

MQTT_CONN_FLAGS_NAME = int('10000000', 2)
MQTT_CONN_FLAGS_PASSWORD = int('01000000', 2)
MQTT_CONN_FLAGS_RETAIN = int('00100000', 2)
MQTT_CONN_FLAGS_QoS = int('00011000', 2)
MQTT_CONN_FLAGS_FLAG = int('00000100', 2)
MQTT_CONN_FLAGS_CLEAN = int('00000010', 2)

MQTT_CONN_FLAGS_SESSION_PRESENT = int('00000001', 2)

MQTT_SUBACK_QoS0 = MQTT_QoS0
MQTT_SUBACK_QoS1 = MQTT_QoS1
MQTT_SUBACK_QoS2 = MQTT_QoS2
MQTT_SUBACK_FAILURE = 0x80


def remaining2list(remain, exception=False):
    bytes_remain = []
    if not exception:
        if remain is None:
            return bytes_remain
        elif remain < 0:
            return bytes_remain
    else:
        if remain is None:
            raise TypeError('None not allowed')
        elif remain < 0:
            raise ValueError('remain must positive')
    dec = int(remain)
    if dec == 0:
        bytes_remain.append(0)
    while dec > 0:
        _enc = int(dec % 128)
        dec = int(dec / 128)
        if dec > 0:
            _enc = int(_enc | 128)
        bytes_remain.append(_enc)
    return bytes_remain


def int2remaining(remain, exception=False):
    if exception:
        if remain is None:
            raise TypeError('None not allowed')
        elif remain < 0:
            raise ValueError('remain must positive')
    bytes_remain = remaining2list(remain)
    fmt = "!"+("B"*len(bytes_remain))
    return struct.pack(fmt, *bytes_remain)


def get_remaining(buff, start_at=0, exception=False):
    if not buff:
        if exception:
            raise TypeError('required Buff')
        return None
    byte_size = struct.calcsize("!B")
    multiplier = 1
    end = start_at
    remain = 0
    try:
        read, = struct.unpack_from("!B", buff, end * byte_size)
        if read <= 0x7f:
            if 1 != len(buff):
                if exception:
                    raise struct.error('Buffer bigger than remain')
                return -1
            return read & 127
        while read > 0x7f:
            remain += (read & 127) * multiplier
            multiplier *= 128
            end += 1
            read, = struct.unpack_from("!B", buff, end * byte_size)
        end += 1
        remain += (read & 127) * multiplier
    except struct.error as ex:
        if exception:
            raise ex
        return -1
    if end != len(buff):
        if exception:
            raise struct.error
        return -1
    return remain


def get_string(buff, exception=False):
    if buff is None:
        if exception:
            raise TypeError('None not allowed')
        return ''
    if not buff or len(buff) < 2:
        if exception:
            raise TypeError('required Buff')
        return None
    str_size, = struct.unpack_from("!H", buff[:2])
    fmt = "!"+("B"*str_size)
    utf8_str = struct.unpack_from(fmt, buff, struct.calcsize("!H"))
    byte_str = map(chr, utf8_str)
    return ''.join(byte_str).decode('utf8')


def gen_string(uni_str, exception=False):
    if uni_str is None:
        if exception:
            raise TypeError('None not allowed')
        return ''
    if not hasattr(uni_str, 'encode'):
        if exception:
            raise TypeError('uni_str required function encode(format)')
        return None
    utf8_str = uni_str.encode('utf8')
    str_size = len(utf8_str)
    fmt = "!H"+("B"*str_size)
    byte_str = map(ord, utf8_str)
    return struct.pack(fmt, str_size, *byte_str)
