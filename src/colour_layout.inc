; One source of truth for Python builders and the colour-bank assembly.
; Scene tables begin at 0x1000 and must end before the fighter catalogue.
%define FIGHTER_PALETTE_BASE 0x2000
; Seventeen record boundaries for the second hash nibble in a CTB4 shard.
%define CLASS_PREFIX_BASE 0x21D0
%define CLASS_TABLE_BASE 0x2200
%define COLOUR_BANK_END 0x10000
; Hash-prefix shard banks are replicated code/data images, mapped through C2.
%define CLASS_SHARD_COUNT 0x10
%define CLASS_SHARD_BANK_BASE 0xD0
; CTB4 workspace, outside the 4bpp mirror and rolling-resync flags.
%define CONTEXT_MAP_BASE 0x8300
%define CONTEXT_MAP_SIZE 0x80
; Fighter owner lease, 0..90. Bit 7 requests the next VBlank transfer.
%define FIGHT_ACTIVITY 0x8204
%define RESYNC_LEFT 0x8200
%define RESYNC_CURSOR 0x8202
