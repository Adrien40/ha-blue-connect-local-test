# Copyright (c) 2026 Adrien40
# SPDX-License-Identifier: GPL-3.0-only

"""Helpers shared by the Hydrao test modules."""


def u16le(value: int) -> tuple[int, int]:
    """Split a 16-bit value into (low_byte, high_byte), little-endian."""
    return value & 0xFF, (value >> 8) & 0xFF


def make_frames(
    total: int, shower: int, duration_ticks: int, temp_c: float
) -> tuple[bytearray, bytearray, bytearray]:
    """Build (vol_data, dur_data, temp_data) BLE frames as the device would
    send them, from human-friendly values.

    `duration_ticks` is the raw uint16 duration counter (1/50 s per tick).
    """
    t_lo, t_hi = u16le(total)
    s_lo, s_hi = u16le(shower)
    vol_data = bytearray([t_lo, t_hi, s_lo, s_hi])

    d_lo, d_hi = u16le(duration_ticks)
    dur_data = bytearray([d_lo, d_hi])

    temp_ticks = round(temp_c * 2)
    tm_lo, tm_hi = u16le(temp_ticks)
    temp_data = bytearray([tm_lo, tm_hi])

    return vol_data, dur_data, temp_data
