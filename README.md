# Void Azul — overlay de live

Identidade visual independente inspirada em Sylvanas e no universo de World of Warcraft: preto, azul-cobalto, azul elétrico e ciano. A personagem e as fissuras ficam nas extremidades; o centro permanece **realmente transparente** para a gameplay. Sem textos, logotipos ou marcas na arte.

## Entrega

| Arquivo | Uso |
| --- | --- |
| **[`overlay_sylvanas_void_4k.png`](overlay_sylvanas_void_4k.png)** | Overlay estático completo: PNG RGBA **3840 × 2160**, 16:9, centro e webcam transparentes. |
| **[`obs_overlay.html`](obs_overlay.html)** | Versão animada discreta, para usar como **Fonte de navegador** no OBS. Usa o mesmo PNG e anima somente as bordas. |
| **[`webcam_void_azul.png`](webcam_void_azul.png)** | Moldura de webcam avulsa, transparente, para usar em outras cenas ou em uma posição personalizada. |
| **[`pacote_void_azul_stream.zip`](pacote_void_azul_stream.zip)** | Arquivos de uso no OBS reunidos em um único download. |

Uma **[prévia interativa](index.html)** permite conferir a arte sobre um cenário demonstrativo, alternar para fundo quadriculado e ligar/desligar a animação. A imagem de gameplay da prévia **não** faz parte do overlay.

## Instalação no OBS Studio

1. Crie uma cena **16:9** (idealmente 3840 × 2160, ou 1920 × 1080 se for transmitir em Full HD).
2. Adicione a captura de jogo e a webcam. Deixe a webcam **abaixo** da moldura na lista de fontes.
3. Escolha **uma** das duas opções para o overlay principal:
   - **Estático:** adicione `overlay_sylvanas_void_4k.png` como **Fonte de imagem**, ajustada ao tamanho da cena.
   - **Animado:** extraia o ZIP mantendo `obs_overlay.html` e `overlay_sylvanas_void_4k.png` **na mesma pasta**. Adicione `obs_overlay.html` como **Fonte de navegador → Arquivo local** e defina largura/altura iguais às da cena (por exemplo, 1920 × 1080). O fundo do HTML é transparente; não é necessário plugin nem conexão com a internet.
4. Em uma cena **4K**, use como ponto de partida para a webcam **X = 2900, Y = 1536, largura = 800, altura = 450 px**. Em **1080p**, divida esses valores por dois: **X = 1450, Y = 768, largura = 400, altura = 225 px**. Faça pequenos ajustes conforme o enquadramento da câmera.

A moldura avulsa `webcam_void_azul.png` é **opcional**: a moldura já está integrada ao overlay principal. Não sobreponha as duas molduras na mesma posição.

## Recriar os PNGs

A pintura-base está em `assets/void_frame_source.png`; o script `tools/build_overlay.py` produz o overlay profissional com máscara alfa e uma webcam menor, além da moldura avulsa:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python tools/build_overlay.py
python3 tools/package.py
```

A arte é uma criação independente; **não é material oficial da Blizzard nem da OWN3D**.
