#!/usr/bin/env python3
"""Toolkit de triagem para CTF (forense de arquivos, cripto simples, binarios).

Uso:
  python ctf_toolkit.py triage  <arquivo>          # tipo real, strings de flag, dados extras, segmentos
  python ctf_toolkit.py strings <arquivo> [regex]  # strings ASCII (filtra por regex)
  python ctf_toolkit.py jpgcom  <arquivo.jpg>      # comentarios/segmentos do JPEG (+ tenta hex/base64)
  python ctf_toolkit.py pngchunks <arquivo.png>    # lista chunks do PNG e dados apos IEND
  python ctf_toolkit.py planes  <imagem> [saida]   # planos de bits (LSB) para inspecao visual
  python ctf_toolkit.py lsb     <imagem> [canais]  # extrai LSB (ex: RGB, R, RGBA) e procura texto
  python ctf_toolkit.py decode  <texto>            # base64 / hex / rot13 / todos os Caesar
  python ctf_toolkit.py rsa     <key.pem> <cifra>  # decifra RSA (PKCS1v15 / OAEP)
  python ctf_toolkit.py disasm  <elf> [hex_ini] [tam]  # desmonta x86-64 (precisa de capstone)

Dependencias: pip install pillow numpy cryptography capstone
"""
import base64
import binascii
import codecs
import re
import struct
import sys

FLAG_RE = re.compile(rb"(?i)(FirstFlag|academy|picoCTF|THM|HTB|flag|css|ctf)\{[^}\n]{1,200}\}")
MAGICS = {
    b"\x89PNG\r\n\x1a\n": "PNG",
    b"\xff\xd8\xff": "JPEG",
    b"GIF8": "GIF",
    b"PK\x03\x04": "ZIP/DOCX/JAR",
    b"Rar!": "RAR",
    b"7z\xbc\xaf": "7z",
    b"\x1f\x8b\x08": "GZIP",
    b"%PDF": "PDF",
    b"\x7fELF": "ELF",
    b"MZ": "PE/EXE",
    b"\x00\x00\x01\x00": "ICO",
    b"SQLite format 3": "SQLite",
    b"BM": "BMP",
}


def read(path):
    with open(path, "rb") as f:
        return f.read()


def real_type(d):
    for sig, name in MAGICS.items():
        if d.startswith(sig):
            return name
    return "desconhecido"


def find_flags(d):
    return [(m.start(), m.group().decode(errors="replace")) for m in FLAG_RE.finditer(d)]


def ascii_strings(d, minlen=6):
    for m in re.finditer(rb"[\x20-\x7e]{%d,}" % minlen, d):
        yield m.start(), m.group().decode()


def cmd_triage(path):
    d = read(path)
    print(f"[+] tamanho: {len(d)} bytes | tipo real (magic bytes): {real_type(d)}")
    print(f"    primeiros bytes: {d[:16].hex()}")
    print("[+] padroes de flag no arquivo bruto:")
    for off, s in find_flags(d) or []:
        print(f"    offset {off}: {s}")
    print("[+] assinaturas de outros formatos embutidas (offset > 0):")
    for sig, name in MAGICS.items():
        if len(sig) < 4 or sig.startswith(b"\x00"):
            continue
        for m in re.finditer(re.escape(sig), d):
            if m.start() > 0:
                print(f"    {name} em {m.start()}")
    if d.startswith(b"\x89PNG"):
        cmd_pngchunks(path)
    elif d.startswith(b"\xff\xd8"):
        cmd_jpgcom(path)


def cmd_strings(path, rx=None):
    d = read(path)
    pat = re.compile(rx) if rx else None
    for off, s in ascii_strings(d):
        if not pat or pat.search(s):
            print(f"{off:#x}: {s}")


def try_decode_blob(b):
    b = b.strip()
    out = []
    try:
        out.append(("hex", binascii.unhexlify(b)))
    except Exception:
        pass
    try:
        out.append(("base64", base64.b64decode(b, validate=True)))
    except Exception:
        pass
    return out


def cmd_jpgcom(path):
    d = read(path)
    o = 2
    print("[+] segmentos JPEG:")
    while o < len(d) and d[o] == 0xFF:
        m = d[o + 1]
        if m == 0xDA:
            print(f"    SOS (dados da imagem) em {o}")
            break
        l = struct.unpack(">H", d[o + 2:o + 4])[0]
        body = d[o + 4:o + 2 + l]
        tag = {0xFE: "COM (comentario)", 0xE0: "APP0/JFIF", 0xE1: "APP1/EXIF-XMP"}.get(m, hex(m))
        print(f"    {tag} em {o}, {l} bytes: {body[:60]!r}")
        if m == 0xFE or m == 0xE1:
            for kind, dec in try_decode_blob(body):
                print(f"      -> decodificado como {kind}: {dec[:120]!r}")
            for off, s in find_flags(body):
                print(f"      -> flag: {s}")
        o += 2 + l
    eoi = d.rfind(b"\xff\xd9")
    print(f"[+] bytes apos o EOI (FFD9): {len(d) - eoi - 2}")


def cmd_pngchunks(path):
    d = read(path)
    o = 8
    print("[+] chunks PNG:")
    while o + 8 <= len(d):
        l = struct.unpack(">I", d[o:o + 4])[0]
        t = d[o + 4:o + 8].decode("ascii", "replace")
        extra = ""
        if t in ("tEXt", "iTXt", "zTXt", "eXIf"):
            extra = repr(d[o + 8:o + 8 + min(l, 200)])
        print(f"    {t} ({l} bytes) {extra}")
        o += 12 + l
        if t == "IEND":
            break
    print(f"[+] bytes apos IEND: {len(d) - o}")
    if len(d) - o > 0:
        print(f"    {d[o:o + 200]!r}")


def cmd_planes(path, out="planes.png"):
    import numpy as np
    from PIL import Image
    im = np.array(Image.open(path).convert("RGB"))
    tiles = [((im[:, :, c] >> b) & 1) * 255 for c in range(3) for b in (0, 1, 2)]
    rows = [np.hstack(tiles[i * 3:i * 3 + 3]) for i in range(3)]
    Image.fromarray(np.vstack(rows).astype("uint8")).save(out)
    print(f"[+] salvo em {out} (linhas R,G,B; colunas bit0,bit1,bit2). Abra e procure formas/texto.")


def cmd_lsb(path, channels="RGB"):
    import numpy as np
    from PIL import Image
    img = Image.open(path).convert("RGBA")
    a = np.array(img)
    idx = {"R": 0, "G": 1, "B": 2, "A": 3}
    sel = [idx[c] for c in channels.upper()]
    bits = (a[:, :, sel] & 1).reshape(-1)
    data = np.packbits(bits).tobytes()
    print(f"[+] {len(data)} bytes extraidos (LSB canais {channels})")
    for off, s in find_flags(data):
        print(f"    flag em {off}: {s}")
    txt = data[:64]
    print(f"    primeiros bytes: {txt!r}")
    print("    (se for lixo aleatorio, provavelmente e so ruido de foto: nao ha LSB stego)")


def caesar(s, k):
    r = []
    for c in s:
        if c.isalpha():
            base = ord("A") if c.isupper() else ord("a")
            r.append(chr((ord(c) - base + k) % 26 + base))
        else:
            r.append(c)
    return "".join(r)


def cmd_decode(text):
    print("[hex]    ", end="")
    try:
        print(binascii.unhexlify(text))
    except Exception:
        print("n/a")
    print("[base64] ", end="")
    try:
        print(base64.b64decode(text, validate=True))
    except Exception:
        print("n/a")
    print("[rot13]  ", codecs.encode(text, "rot_13"))
    for k in range(1, 26):
        s = caesar(text, -k)
        mark = "  <== " if re.search(r"(?i)(first|flag|ctf|academy|thm|picoctf)", s) else "     "
        print(f"[caesar -{k:2}]{mark}{s}")


def cmd_rsa(pem_path, ct_path):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    key = load_pem_private_key(read(pem_path), None)
    ct = read(ct_path)
    opts = {
        "PKCS1v15": padding.PKCS1v15(),
        "OAEP-SHA1": padding.OAEP(padding.MGF1(hashes.SHA1()), hashes.SHA1(), None),
        "OAEP-SHA256": padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), None),
    }
    for name, pad in opts.items():
        try:
            print(name, key.decrypt(ct, pad))
        except Exception:
            print(name, "falhou")


def cmd_disasm(path, start=None, size=0x200):
    from capstone import CS_ARCH_X86, CS_MODE_64, Cs
    d = read(path)
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    s = int(start, 16) if start else 0x1000
    for i in md.disasm(d[s:s + int(size, 16) if isinstance(size, str) else s + size], s):
        print(f"{i.address:#x}  {i.mnemonic:6} {i.op_str}")
    print("\nDica: enderecos 'lea reg,[rip+X]' apontam para .rodata: endereco = (prox instrucao) + X.")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    cmd, args = sys.argv[1], sys.argv[2:]
    fn = {
        "triage": cmd_triage, "strings": cmd_strings, "jpgcom": cmd_jpgcom,
        "pngchunks": cmd_pngchunks, "planes": cmd_planes, "lsb": cmd_lsb,
        "decode": cmd_decode, "rsa": cmd_rsa, "disasm": cmd_disasm,
    }.get(cmd)
    if not fn:
        print(__doc__)
        return
    fn(*args)


if __name__ == "__main__":
    main()
