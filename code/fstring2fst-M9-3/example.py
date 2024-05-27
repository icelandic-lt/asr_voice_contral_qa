from fstring2fst.fstring2fst import create_fst, generate

VARIABLES = {
    "digit1": ["a", "x"],
    "digit2": ["b", "y"],
    "digit3": ["c", "z"],
}
seq = [
    "{digit1}-{digit2}-{digit3}",
]
pattern = [
    "e{seq}{seq}e",
    "r{seq}{seq}r",
]
SENTENCES = {
    "seq": seq,
    "row": pattern,
}
OUTPUT = "row"


if __name__ == "__main__":
    f, ist, ost = create_fst(VARIABLES, SENTENCES, OUTPUT)

    f.write("example.fst")
    ist.write_text("isyms.txt")
    ost.write_text("osyms.txt")
    f.draw("example.gv")
    # dot -Tps test.gv -o outfile.ps
    # fstdraw lexicon_opt.fst | dot -Tjpg >Mars.jpg
    # fstrmepsilon binary.fst | fstdeterminize | fstminimize > binary_opt.fst
    generate(f)
