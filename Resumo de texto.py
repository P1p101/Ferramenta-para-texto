import requests
from bs4 import BeautifulSoup
import nltk
import string
import heapq
from nltk.corpus import stopwords
from deep_translator import GoogleTranslator

# Download dos recursos necessários do NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Função para preprocessamento do texto
def preprocessamento(texto):
    stopwords_pt = stopwords.words('portuguese')
    pontuation = string.punctuation
    texto_formatado = texto.lower()
    tokens = nltk.word_tokenize(texto_formatado)
    tokens = [palavra for palavra in tokens if palavra not in stopwords_pt and palavra not in pontuation]
    texto_formatado = ' '.join([str(elemento) for elemento in tokens if not elemento.isdigit()])
    return texto_formatado

# Função para traduzir texto
def traduzir_texto(texto, idioma_destino):
    try:
        return GoogleTranslator(source='auto', target=idioma_destino).translate(texto)
    except Exception as e:
        print(f"Erro ao traduzir texto: {e}")
        return texto

# Função para gerar resumo
def gerar_resumo(texto, url_pagina, num_frases=20):
    # Pré-processamento do texto
    texto_formatado = preprocessamento(texto)

    # Calcular a frequência das palavras
    frequencia_palavras = nltk.FreqDist(nltk.word_tokenize(texto_formatado))
    frequencia_maxima = max(frequencia_palavras.values())

    # Calcular a frequência proporcional
    frequencia_proporcional = {palavra: (frequencia / frequencia_maxima) for palavra, frequencia in frequencia_palavras.items()}

    # Tokenizar as frases
    lista_frases = nltk.sent_tokenize(texto)

    # Notar as frases
    nota_frases = {}
    for frase in lista_frases:
        for palavra in nltk.word_tokenize(frase.lower()):
            if palavra in frequencia_palavras.keys():
                if frase not in nota_frases.keys():
                    nota_frases[frase] = frequencia_palavras[palavra]
                else:
                    nota_frases[frase] += frequencia_palavras[palavra]

    # Selecionar as melhores frases
    numero_frases = min(len(lista_frases) // 3, num_frases)  # Ajustar o número de frases no resumo
    melhores_frases = heapq.nlargest(numero_frases, nota_frases, key=nota_frases.get)
    resumo = ' '.join(melhores_frases)

    # Extrair as URLs de imagens da página
    response = requests.get(url_pagina)
    soup = BeautifulSoup(response.content, 'html.parser')
    imagens = soup.find_all('img')
    imagens_html = ''
    for idx, img in enumerate(imagens):
        if idx >= 1 and idx <= 2:  # Captura da segunda até a quarta imagem (índices 1, 2 e 3)
            imagem_url = img['src']
            imagens_html += f"<div style='display:inline-block; margin-right:50px;'><img src='{imagem_url}' alt='Imagem' style='display:block; margin:auto; width:300px; height:400px;'></div>"

    # Exibir o resumo em HTML (marcando as frases do resumo e exibindo as imagens)
    texto_html = ' '.join([f"<mark>{frase}</mark>" if frase in melhores_frases else frase for frase in lista_frases])
    imagens_html = f"<div style='text-align:center; margin-top:40px;'>{imagens_html}</div>"

    # Salvar o resumo formatado em um arquivo HTML
    with open('summarize.html', 'w', encoding='utf-8') as file:
        file.write(f"<html><body>"
                   f"<h1 style='text-align:center;'>Resumo do texto</h1>"
                   f"{texto_html}"
                   f"<br>{imagens_html}"
                   f"</body></html>")

    print("Resumo salvo no arquivo 'summarize.html'")
    return resumo

# Função principal para processar a URL
def processar_url(url, idioma='pt', nivel_detalhamento=20):
    try:
        # Baixar o conteúdo da página
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extrair o texto dos parágrafos da página
        texto_original = ' '.join([paragrafo.get_text() for paragrafo in soup.find_all('p')])

        # Verificar o idioma do texto original e traduzir se necessário
        if idioma != 'pt':
            texto_original = traduzir_texto(texto_original, idioma)

        # Dividir o texto em partes menores para tradução
        partes_texto = nltk.sent_tokenize(texto_original)
        texto_traduzido = ' '.join([traduzir_texto(part, 'pt') for part in partes_texto])

        resumo = gerar_resumo(texto_traduzido, url, num_frases=nivel_detalhamento)

        print(f'\nResumo do texto:\n{resumo}')
    except Exception as e:
        print(f"Erro ao processar URL: {e}")

# URL do site a ser processado
url = 'INSIRA O LINK DO SITE AQUI'
idioma = 'pt'  # Idioma para tradução, 'pt' para manter em português
nivel_detalhamento = 20  # Número de frases no resumo

# Chamar a função principal com a URL e as configurações
processar_url(url, idioma, nivel_detalhamento)
