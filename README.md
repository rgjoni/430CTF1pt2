# csci430 - CTF1 bank app (flask version)

## how to install

you will need:

- python3
- pip3




you may or may not have to do the following:

- `sudo apt update`
- `sudo apt install python3.6`
- `sudo apt install python3-pip`
- `pip3 install flask`
- `pip3 install passlib`

note that on deterlab, you need to use `pip3` slightly differently. see piazza
for details. i will not describe it here, for security reasons

also, you can use a higher version of python. the only reason i wrote `3.6` in
the  list above is because that's what's on our deterlab node




## how to run

to run, do
`python3 main.py`




--------------------------------------------------------------------------------




## notes

### database reset warning

note that the database is reset every time you restart the server. this is okay,
since this is just a CTF exercise for class, and we dont really need to store
all of that info




### type checking on transaction amounts

the server checks if a transaction amount is valid by first checking if it's a
"valid number". the input is taken as a string, and up to 1 decimal point is
removed. then it checks if all the characters are 0-9 using `isdecimal()`.
although this is not the most "pythonic" way of doing things (i.e. we're not
doing a cast in a try-except block), this technique works for our purposes. it
results in the following:

**allowed**

- `123`
- `123.456`
- `123.`
- `.456`
- numbers in other unicode fonts (e.g. １２３)
- `0`

**not allowed**

- letters
- special characters (other than a single decimal point)
- empty string
- whitespace (even if it would be valid otherwise)
- negative numbers
- any usage of the `-` symbol (e.g. `--123`)
- complex numbers
- scientific notation
- fractions
- numerical superscripts and subscripts
- roman numerals
- numbers with multiple decimal points
- decimal point(s) without any numbers
- `True` or `False`
- `NaN`
- `inf` and `-inf`
- emojis (including ones that depict numbers)

this is all done using `is_valid_amount()`. after this, you still need to cast
the string to a number, round to 2 decimal places, and (if you're doing a
withdrawal) check if there's enough money in the account.

also note that `isdecimal()` is not the same as `isdigit()`. it would seem that
`isdecimal()` allows for a few special characters other than `0123456789`. these
appear to be unicode values for numbers in other languages. this includes
numbers in "vaporwave font" (e.g. １２３). however, python3 appears to handle
these just like regular numbers, so i dont really see a point in trying to block
these

if it's a decimal, it gets rounded to the nearest integer anyways. not sure if
we need to allow for non integer amounts, but i kept `is_valid_amount()` as a
separate function just in case we do. but be aware that `round()` in python
works kinda weird. if you try to deposit/withdraw `0.5`, it will **not** be
interpreted as `1` when rounded. if we do end up having to support decimals, we
should use the `Decimal` object (comes with python3)

if you need any more info about the type checking, contact me (audrey)




## duplicate query parameters

it seems that flask automatically handles duplicates, and only chooses the first
one. so if you do something like:

    localhost:5000/blue/manage?action=deposit&action=withdraw&amount=123

you will deposit $123 (and nothing else happens)

