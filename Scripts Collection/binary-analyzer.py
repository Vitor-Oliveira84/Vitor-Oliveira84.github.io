#!/usr/bin/env python3
"""Binary Analyzer - Análise profunda de executáveis e binários.

Uso:
  python binary-analyzer.py <elf/exe>           # Análise completa
  python binary-analyzer.py <binary> --strings  # Apenas strings interessantes
  python binary-analyzer.py <binary> --disasm   # Desassembly da seção .text
  python binary-analyzer.py <binary> --sections # Info sobre seções
  python binary-analyzer.py <binary> --verbose  # Output detalhado

Dependências:
  pip install capstone
  (opcional: python-magic para detecção de tipo)
"""
import sys
import re
import struct
import os

try:
    from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CS_MODE_32
    HAS_CAPSTONE = True
except:
    print("⚠️  capstone não instalado: pip install capstone")
    HAS_CAPSTONE = False

class BinaryAnalyzer:
    def __init__(self, filepath, verbose=False):
        self.filepath = filepath
        self.verbose = verbose
        self.data = None
        self.findings = []

        if not os.path.exists(filepath):
            print(f"❌ Arquivo não encontrado: {filepath}")
            sys.exit(1)

        with open(filepath, 'rb') as f:
            self.data = f.read()

    def analyze(self):
        """Análise completa."""
        print(f"\n{'='*70}")
        print(f"🔬 Analisando: {os.path.basename(self.filepath)} ({len(self.data)} bytes)")
        print(f"{'='*70}\n")

        self._detect_type()
        self._extract_strings()
        self._analyze_structure()

        if HAS_CAPSTONE and '--disasm' not in sys.argv:
            self._disassemble_main()

    def _detect_type(self):
        """Detecta tipo do binário."""
        print(f"📋 TIPO DE ARQUIVO:")
        if self.data.startswith(b'\x7fELF'):
            print(f"  ✅ ELF (Linux/Unix)")
            self._parse_elf_header()
        elif self.data.startswith(b'MZ'):
            print(f"  ✅ PE/EXE (Windows)")
            self._parse_pe_header()
        else:
            print(f"  ⚠️  Desconhecido (magic: {self.data[:4].hex()})")

    def _parse_elf_header(self):
        """Parse do header ELF."""
        if len(self.data) < 64:
            return

        ei_class = self.data[4]  # 1=32-bit, 2=64-bit
        ei_data = self.data[5]   # 1=little-endian, 2=big-endian
        ei_version = self.data[6]
        ei_osabi = self.data[7]

        arch = "64-bit" if ei_class == 2 else "32-bit"
        endian = "little-endian" if ei_data == 1 else "big-endian"

        print(f"  • Arquitetura: {arch}")
        print(f"  • Endianness: {endian}")

        # Entry point
        if ei_class == 2:  # 64-bit
            entry = struct.unpack('<Q', self.data[32:40])[0]
        else:
            entry = struct.unpack('<I', self.data[28:32])[0]

        print(f"  • Entry Point: 0x{entry:x}")
        self.findings.append(("ELF Entry", f"0x{entry:x}"))

    def _parse_pe_header(self):
        """Parse do header PE."""
        if len(self.data) < 64:
            return

        pe_offset = struct.unpack('<I', self.data[0x3c:0x40])[0]
        if pe_offset + 24 > len(self.data):
            return

        machine = struct.unpack('<H', self.data[pe_offset+4:pe_offset+6])[0]
        machines = {0x14c: "i386", 0x8664: "x64", 0xaa64: "ARM64"}

        print(f"  • Arquitetura: {machines.get(machine, f'0x{machine:x}')}")

    def _extract_strings(self):
        """Extrai strings ASCII interessantes."""
        print(f"\n🔐 STRINGS INTERESSANTES:")

        patterns = [
            (r'(?i)(password|passwd|pwd)', 'Senha'),
            (r'(?i)(admin|user|login)', 'Credenciais'),
            (r'(?i)(flag|FLAG|secret)', 'Flag/Secret'),
            (r'(?i)(key|token|auth)', 'Autenticação'),
            (r'(?i)(url|http|api)', 'URLs/APIs'),
            (r'(?i)(error|exception|fail)', 'Mensagens'),
        ]

        found_any = False
        for m in re.finditer(rb'[\x20-\x7e]{6,}', self.data):
            s = m.group().decode(errors='replace')

            for pattern, category in patterns:
                if re.search(pattern, s):
                    if not found_any:
                        found_any = True
                    print(f"  📌 [{category:15}] {s[:70]}")
                    self.findings.append((category, s))
                    break

        if not found_any:
            print(f"  ⚠️  Nenhuma string interessante encontrada")

    def _analyze_structure(self):
        """Analisa estrutura do binário."""
        print(f"\n🏗️  ESTRUTURA:")

        # Procura por seções comuns
        sections = {
            b'.text': 'Código executável',
            b'.data': 'Dados inicializados',
            b'.rodata': 'Dados somente-leitura',
            b'.bss': 'Dados não-inicializados',
            b'.stack': 'Stack',
            b'.symtab': 'Tabela de símbolos',
            b'.strtab': 'Tabela de strings',
        }

        for section, desc in sections.items():
            if section in self.data:
                offset = self.data.find(section)
                print(f"  ✅ {section.decode()}: encontrada em offset 0x{offset:x}")

    def _disassemble_main(self):
        """Desassembla função main se encontrada."""
        if not HAS_CAPSTONE:
            return

        print(f"\n🔧 DESASSEMBLY:")

        # Busca por "main" string
        main_offsets = []
        for m in re.finditer(b'main\x00', self.data):
            main_offsets.append(m.start())

        if self.data.startswith(b'\x7fELF'):
            # Para ELF, tenta seção .text
            text_offset = self.data.find(b'.text')
            if text_offset > 0:
                # Tenta começar em pontos prováveis
                for start_offset in [0x1000, 0x400, 0x1160]:
                    if start_offset < len(self.data):
                        self._disasm_region(start_offset, 0x200)
                        break

    def _disasm_region(self, offset, size):
        """Desassembla uma região."""
        if not HAS_CAPSTONE:
            return

        try:
            md = Cs(CS_ARCH_X86, CS_MODE_64)
            region = self.data[offset:offset+size]

            print(f"  📍 Offset 0x{offset:x}:")
            for instr in md.disasm(region, offset):
                print(f"     0x{instr.address:x}: {instr.mnemonic} {instr.op_str}")

                # Procura por padrões interessantes
                if 'scanf' in instr.op_str or 'printf' in instr.op_str:
                    print(f"        ⚠️  I/O suspeito!")
                elif 'strcmp' in instr.op_str or 'cmp' in instr.mnemonic:
                    print(f"        🔍 Comparação detectada")
        except Exception as e:
            if self.verbose:
                print(f"  ❌ Erro no desassembly: {e}")

    def report(self):
        """Relatório final."""
        if self.findings:
            print(f"\n{'='*70}")
            print(f"📊 ACHADOS:")
            print(f"{'='*70}")
            for key, value in self.findings[:15]:
                print(f"  • {key}: {str(value)[:80]}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    filepath = sys.argv[1]
    verbose = '--verbose' in sys.argv

    analyzer = BinaryAnalyzer(filepath, verbose=verbose)
    analyzer.analyze()
    analyzer.report()

if __name__ == "__main__":
    main()
