; One source of truth for Python builders and the colour-bank assembly.
; Scene tables begin at 0x1000 and must end before the fighter catalogue.
%define FIGHTER_PALETTE_BASE 0x2000
%define CLASS_TABLE_BASE 0x2200
%define COLOUR_BANK_END 0x10000
; Hash-prefix shard banks are replicated code/data images, mapped through C2.
%define CLASS_SHARD_COUNT 0x10
%define CLASS_SHARD_BANK_BASE 0xD0
