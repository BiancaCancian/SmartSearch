## Visão Geral do Projeto

### O foco deste projeto foi o desenvolvimento de uma solução de busca inteligente de PCs, com o objetivo de otimizar tempo na tomada de decisão e facilitar a identificação do equipamento Advantech mais adequado para cada cenário.

### A solução utiliza conceitos de Inteligência Artificial, dessa forma, é possível compreender melhor:

- As linhas de PCs Advantech

- Os casos de uso específicos de cada equipamento

- As características técnicas mais relevantes para cada aplicação

### O projeto simula como um cliente descreve um problema real, por exemplo, visão computacional em ambiente industrial, e a aplicação traduz isso em requisitos tecnicos, sugerindo o hardware Advantech mais adequado. 
<img width="1348" height="595" alt="image" src="https://github.com/user-attachments/assets/6aa73a3e-03ac-4ff4-8ffb-907935aa9fe5" />

![alt text](image.png)

##  Pré-requisitos

Antes de iniciar, certifique-se de ter os seguintes itens instalados em sua máquina:

* **Python** (preferencialmente a mesma versão utilizada no projeto)
* **Node.js**
* **Visual Studio Code (VS Code)**
* **Git**

###  Verificando versões

No terminal ou prompt de comando, execute:

```bash
py --version
node -v
```

---

##  Clonando o repositório

```bash
git clone <URL_DO_REPOSITORIO>
```

Após clonar:

1. Abra o **VS Code**
2. Selecione **File > Open Folder**
3. Abra a pasta do projeto clonado

---

##  Configurando o ambiente Python (Backend)

###  Acessar a pasta principal do projeto

```bash
cd C:\Users\bianc\Downloads\Advantech\Advantech-main
```

> Ajuste o caminho conforme o local onde o projeto foi clonado.

###  Criar o ambiente virtual

```bash
py -m venv venv
```

###  Ativar o ambiente virtual

```bash
.\venv\Scripts\activate
```

---

## Instalando dependências do backend

Com o ambiente virtual ativo, execute:

```bash
pip install fastapi uvicorn pydantic sentence-transformers faiss-cpu numpy
```

### Executar o servidor backend

```bash
uvicorn main:app --reload
```

O backend estará disponível em:

```
http://localhost:8000
```

###  Encerrar o ambiente virtual

```bash
deactivate
```

---

##  Configurando o Frontend

### Acessar a pasta do frontend

```bash
cd C:\Users\bianc\Downloads\Advantech\Advantech-main\frontend
```

###  Instalar dependências do Node.js

```bash
npm install
```

###  Executar o frontend

```bash
npm run dev
```

O frontend estará disponível no endereço exibido no terminal (geralmente `http://localhost:5173`).


