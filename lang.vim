" Vim syntax file
" Language: Lang

if exists("b:current_syntax")
	finish
endif

syntax keyword langKeyword fn do while if else return let include
syntax region langComment start="//" end="$"
syntax region langString start=/\v"/ end=/\v"/ skip=/\v\\./

" numbers
syntax match langNumberDecimal "\<[0-9]\+\>"
syntax match langNumberBinary "\<0b[0-1]\+\>"
syntax match langNumberOctal "\<0o[0-7]\+\>"
syntax match langNumberHexadecimal "\<0x[0-9abcdefABCDEF]\+\>"

syntax keyword langConstant nil false true

hi def link langKeyword Keyword
hi def link langComment Comment
hi def link langString String
hi def link langNumberDecimal Number
hi def link langNumberBinary Number
hi def link langNumberOctal Number
hi def link langNumberHexadecimal Number
hi def link langConstant Constant

let b:current_syntax = "lang"

