# -*- coding: utf-8 -*-
import openai
import subprocess
import os

from openai import OpenAI

client = OpenAI(api_key="xxx")

def gerar_codigo():
    """
    Agente de IA que auxilia na geração e correção de códigos Python.
    """
    print("Olá! Sou seu assistente de código. Descreva o que você precisa que eu programe.")
    descricao = input("Descrição: ")

    # Pergunta se o usuário tem um output esperado
    print("Você tem um output esperado para este código? (sim/não)")
    tem_output = input("Resposta: ").strip().lower()

    output_esperado = None
    if tem_output == 'sim':
        print("Por favor, insira o output esperado:")
        print("(Digite 'FIM' em uma nova linha para finalizar a entrada)")
        linhas_output = []
        while True:
            linha = input()
            if linha.strip().upper() == 'FIM':
                break
            linhas_output.append(linha)
        output_esperado = '\n'.join(linhas_output)

    tentativas = 0
    max_tentativas = 5
    codigo_anterior = ""
    resultado_erro = 0
    mensagens = [
        {"role": "system", "content": "Você é um assistente que gera códigos Python de acordo com a descrição do usuário. O código deve estar livre de erros de execução e atender ao output esperado, se fornecido. Se requisitado para criar outro agente ou algum recurso que dependa da API da OpenAI, importe o arquivo env.py e utilize a chave the API da OpenAI da variável api_key. Utilize 'from openai import OpenAI' para importar a biblioteca da openai e 'client.chat.completions.create' para fazer a chamada e 'resposta.choices[0].message.content' para extrair o conteúdo da resposta"},
    ]

    while tentativas < max_tentativas:
        tentativas += 1
        if tentativas == 1:
            # Primeira tentativa: gera o código a partir da descrição
            mensagens.append({"role": "user", "content": f"Desenvolva um código Python que atenda à seguinte descrição: {descricao}"})
            if output_esperado:
                mensagens.append({"role": "user", "content": f"O código deve produzir o seguinte output quando executado:\n{output_esperado}"})
        else:
            # Nas tentativas subsequentes, inclui o código anterior e o erro/output
            mensagens.append({"role": "user", "content": f"O código anterior apresentou o seguinte erro/output:\n{resultado_erro}\nPor favor, corrija o código considerando essas informações."})

        # Chamada à API da OpenAI para gerar o código
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=mensagens,
            max_tokens=1500,
            n=1,
            stop=None,
            temperature=0,
        )

        #print(resposta)
        codigo_gerado = resposta.choices[0].message.content

        # Extrai o código da resposta (caso esteja entre blocos de código)
        if "```" in codigo_gerado:
            codigo_gerado = codigo_gerado.split("```")[1]
            if codigo_gerado.startswith("python"):
                codigo_gerado = codigo_gerado[len("python"):].strip()

        # Salva o código em um arquivo
        nome_arquivo = "codigo_gerado.py"
        with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write(codigo_gerado)

        # Tenta executar o código e captura erros/output
        try:
            resultado = subprocess.check_output(["python", nome_arquivo], stderr=subprocess.STDOUT, text=True)
            resultado_erro = ""
        except subprocess.CalledProcessError as e:
            resultado = ""
            resultado_erro = e.output

        # Verifica se houve erro
        if resultado_erro:
            print(f"Tentativa {tentativas}: O código gerado apresentou erros.")
            codigo_anterior = codigo_gerado
            continue
        else:
            # Se não houve erro, verifica se o output corresponde ao esperado (se fornecido)
            if output_esperado and output_esperado.strip() != resultado.strip():
                print(f"Tentativa {tentativas}: O código não produziu o output esperado.")
                resultado_erro = f"O output obtido foi:\n{resultado}\nMas o output esperado era:\n{output_esperado}"
                codigo_anterior = codigo_gerado
                continue
            else:
                print(f"O código foi gerado com sucesso na tentativa {tentativas}!")
                print("O código está pronto para uso e foi salvo como 'codigo_gerado.py'.")
                break
    else:
        print("Não foi possível gerar um código funcional dentro do número máximo de tentativas.")

if __name__ == "__main__":
    gerar_codigo()
