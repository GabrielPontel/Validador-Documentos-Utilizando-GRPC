# GBProtocol gRPC: Validador de Documentos

Validador de CPF e CNPJ implementado com **gRPC**, com servidor em **Python** e cliente em **Node.js**.

Trabalho da disciplina de Sistemas Distribuídos. Esta é a segunda versão do GBProtocol: a primeira usava sockets TCP com mensagens em texto no formato `(campo,resposta)`. Aqui a comunicação passou a ser feita por gRPC, com o contrato definido em Protocol Buffers.

## Como funciona

O cliente chama o método remoto `Validar` informando o tipo e o número do documento. O servidor aplica as regras de validação e devolve se o documento é válido e, quando houver, um código de erro. O cliente traduz esse código em uma mensagem para o usuário.

```
cliente.js (Node.js)  --- Validar(tipo_doc, doc) --->  servidor.py (Python)
                      <--- (valido, erro) ----------
```

Os dois lados leem o mesmo arquivo `validadordocumento.proto`, por isso conseguem conversar mesmo sendo escritos em linguagens diferentes.

## Contrato (`validadordocumento.proto`)

```proto
syntax = "proto3";

package validadordocumento;

service ValidadorDocumentos {
  rpc Validar (DocumentoRequest) returns (ResultadoResponse);
}

message DocumentoRequest {
  int32 tipo_doc = 1;  // 1 = CPF, 2 = CNPJ
  string doc = 2;
}

message ResultadoResponse {
  bool valido = 1;
  double erro = 2;
}
```

### Requisição

| Campo | Tipo | Descrição |
|---|---|---|
| `tipo_doc` | int32 | 1 = CPF, 2 = CNPJ. O valor 0 significa que o campo não foi informado |
| `doc` | string | Número do documento, somente dígitos |

### Resposta

| Campo | Tipo | Descrição |
|---|---|---|
| `valido` | bool | `true` se o documento é válido |
| `erro` | double | 0 quando não houve erro, ou o código do erro |

### Códigos de resposta

| valido | erro | Significado |
|---|---|---|
| 1 | 0 | Documento válido |
| 0 | 0 | Formato correto, mas os dígitos verificadores não conferem |
| 0 | 1.1 | Estrutura da requisição inválida |
| 0 | 1.2 | Tipo de documento não informado |
| 0 | 1.3 | Documento não informado |
| 0 | 2.1 | Tipo de documento não processado |
| 0 | 3.1 | Quantidade de dígitos menor que a esperada |
| 0 | 3.2 | Quantidade de dígitos maior que a esperada |
| 0 | 4.1 | Documento contém caracteres que não são dígitos |

Neste projeto as mensagens são representadas no formato `campo+resposta`, com os pares separados por `&`. Por exemplo, `tipo_doc+1&doc+52998224725` → `valido+1&erro+0`. É assim que o servidor as mostra no terminal.

## Estrutura do projeto

```
.
├── servidor/
│   ├── validadordocumento.proto
│   ├── servidor.py
│   ├── validadordocumento_pb2.py        (gerado)
│   └── validadordocumento_pb2_grpc.py   (gerado)
└── cliente/
    ├── cliente.js
    └── package.json
```

## Pré-requisitos

- Python 3.7 ou superior
- Node.js 18 ou superior

## Como executar

Os comandos abaixo são para o PowerShell no Windows. No Linux ou macOS, troque `.\venv\Scripts\activate` por `source venv/bin/activate`.

### Servidor (Python)

```powershell
cd servidor
python -m venv venv
.\venv\Scripts\activate
python -m pip install grpcio grpcio-tools
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. validadordocumento.proto
python servidor.py
```

Saída esperada:

```
Servidor iniciado, escutando na porta 4851
```

Deixe esse terminal aberto. Para encerrar o servidor, use `Ctrl+C`.

### Cliente (Node.js)

Em outro terminal:

```powershell
cd cliente
npm install
node cliente.js
```

Exemplo de uso:

```
Tipo (1 = CPF, 2 = CNPJ, 0 = sair): 1
Documento: 52998224725
Resposta: Documento válido
Tipo (1 = CPF, 2 = CNPJ, 0 = sair): 2
Documento: 11.222.333/0001-81
Resposta: Caractere inválido no documento
Tipo (1 = CPF, 2 = CNPJ, 0 = sair): 0
```

## Documentos para teste

| Tipo | Número | Resultado |
|---|---|---|
| CPF | 52998224725 | válido |
| CPF | 52998224726 | inválido |
| CNPJ | 11222333000181 | válido |
| CNPJ | 11222333000180 | inválido |

## Referências

- [gRPC: Quick start em Python](https://grpc.io/docs/languages/python/quickstart/)
- [gRPC: Basics tutorial em Node.js](https://grpc.io/docs/languages/node/basics/)
- [Protocol Buffers: guia da linguagem proto3](https://protobuf.dev/programming-guides/proto3)

## Autor

Gabriel Pontel de Mori
