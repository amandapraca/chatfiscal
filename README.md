# chatfiscal
Agente fiscal inteligente para análise de notas fiscais com Streamlit.

ChatFiscal — Agente Inteligente para Auditoria de Notas Fiscais
O ChatFiscal é um aplicativo interativo desenvolvido com Streamlit que simula um agente fiscal inteligente. Ele analisa arquivos de notas fiscais (CSV ou XML), detecta inconsistências, responde perguntas em linguagem natural e gera gráficos e relatórios automáticos.

O agente fiscal é capaz de:
•	Ler arquivos CSV e XML com dados fiscais
•	Detectar colunas como valor, emitente, data e CFOP automaticamente
•	Responder perguntas como:
o	Qual emitente tem maior valor?
o	Qual CFOP mais utilizado?
o	Qual o faturamento por mês?
•	Realizar auditorias automáticas:
o	Valores negativos
o	CFOPs inválidos
o	Notas sem emitente
•	Gerar gráficos interativos com filtros
•	Exportar relatórios e histórico de perguntas

🧠 Funcionalidades Principais

Aba: Dados & Perguntas
Descrição: Upload de arquivos, visualização dos dados e campo para perguntas ao agente

Aba: Histórico
Descrição: Registro das perguntas e respostas feitas ao agente, com opção de exportar

Aba: Auditoria
Descrição: Verificação automática de inconsistências fiscais

Aba: Visualizações
Descrição: Gráficos interativos com filtros por período, CFOP e emitente

Aba: Painel Inteligente
Descrição: Destaques automáticos, alertas e análises personalizadas via comando

Estrutura do Código
1.	carregar_arquivo(arquivo)
Lê arquivos .csv ou .xml e retorna um DataFrame com os dados fiscais.

2.	detectar_coluna(df, alternativas)
Detecta automaticamente colunas com nomes variados (ex: "valor", "vl_total", "total").

3.	gerar_resposta_llm(pergunta, df)
Gera respostas inteligentes com base na pergunta do usuário e nos dados carregados.

4.	Simulação de dados
Gera 200 notas fiscais fictícias com valores, datas, CFOPs e emitentes aleatórios.

5.	Auditoria fiscal
Detecta automaticamente:
o	Valores negativos
o	CFOPs com formato inválido
o	Notas sem emitente

6.	Visualizações
Gera gráficos de faturamento mensal, ranking de emitentes e permite exportar os dados filtrados.

7.	Painel Inteligente
Exibe destaques automáticos, alertas e permite comandos personalizados.

8.	Histórico
Armazena todas as perguntas e respostas feitas ao agente, com opção de exportar como .docx.

## 🚀 Como Executar o Projeto

### 🔧 Requisitos
- Python 3.8+
- Docker (opcional, para execução via container)

### 🖥️ Execução Local
1. Clone o repositório:
   ```bash
   git clone https://github.com/amandapraca/chatfiscal.git
   cd chatfiscal
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o aplicativo:
   ```bash
   streamlit run app.py
   ```

4. Acesse o aplicativo no navegador em: `http://localhost:8501`

### 🐳 Execução com Docker
1. Construa a imagem Docker:
   ```bash
   docker-compose build
   ```

2. Inicie o container:
   ```bash
   docker-compose up
   ```

3. Acesse o aplicativo no navegador em: `http://localhost:8501`

4. Para parar o container:
   ```bash
   docker-compose down
   ```

## 📂 Exemplos de Arquivos

### Exemplo de Arquivo CSV
```csv
Emitente,Data,Valor,CFOP
Empresa A,2025-10-01,1000.00,5102
Empresa B,2025-10-02,-500.00,6101
Empresa C,2025-10-03,200.00,INVALIDO
```

### Exemplo de Arquivo XML
```xml
<NotasFiscais>
    <Nota>
        <Emitente>Empresa A</Emitente>
        <Data>2025-10-01</Data>
        <Valor>1000.00</Valor>
        <CFOP>5102</CFOP>
    </Nota>
    <Nota>
        <Emitente>Empresa B</Emitente>
        <Data>2025-10-02</Data>
        <Valor>-500.00</Valor>
        <CFOP>6101</CFOP>
    </Nota>
    <Nota>
        <Emitente>Empresa C</Emitente>
        <Data>2025-10-03</Data>
        <Valor>200.00</Valor>
        <CFOP>INVALIDO</CFOP>
    </Nota>
</NotasFiscais>
```

Requisitos
•	Python 3.8 ou superior
•	Navegador moderno (Chrome, Firefox, Edge)

Instalação
1.	Clone o repositório: git clone (https://github.com/amandapraca/chatfiscal.git)
cd chatfiscal
2.	Crie um ambiente virtual (opcional): python -m venv venv
source venv/bin/activate (Linux/macOS)
venv\Scripts\activate (Windows)
3.	Instale as dependências: pip install -r requirements.txt
ou
pip install streamlit pandas numpy python-docx

4.	🚀 Como Executar
1.	Instale as dependências:
pip install streamlit pandas numpy python-docx 
2.	Execute o app:
streamlit run app.py 
3.	Acesse no navegador:
http://localhost:8501 

Formatos Suportados
•	Arquivos .csv com separador automático
•	Arquivos .xml com estrutura baseada em 

Importações utilizadas
•	streamlit
•	pandas
•	numpy
•	xml.etree.ElementTree
•	unicodedata
•	random
•	datetime
•	io
•	python-docx

Tratamento de Erros
•	O app nunca quebra com arquivos incompletos
•	Usa st.stop() para interromper execuções inválidas com segurança
•	Mensagens amigáveis orientam o usuário em caso de erro
