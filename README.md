# FN-Notify-Feasible

[![Build Status](https://travis-ci.org/radar-pi/fn-notify-feasible.svg?branch=develop)](https://travis-ci.org/radar-pi/fn-notify-feasible)
[![Maintainability](https://api.codeclimate.com/v1/badges/f6660230a65774c69610/maintainability)](https://codeclimate.com/github/radar-pi/fn-notify-feasible/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/f6660230a65774c69610/test_coverage)](https://codeclimate.com/github/radar-pi/fn-notify-feasible/test_coverage)

A **Função Notify Feasible** é a função responsável por receber as informações da infração e notificar a possibilidade de ter se tornado um acidente. O modelo atual é baseado em estudos empíricos acerca da velocidade na probabilidade de acidentes. O modelo deve ser melhorado ao longo da vida do radar com o auxílio de um modelo de _data mining_.

## Parâmetros

Os parâmetros da função fn-notify-feasible seguem o modelo de dados do pacote (_package_) de mensagens da arquitetura do sistema do radar. Eles consistem em um objeto JSON com o seguinte formato:

- **id**: Um UUID para identificar unicamente aquele pacote (tipo `string`).

- **type**: Qual o tipo da chamada de função, para que a função possa identificar se o pacote que ele recebeu é do seu domínio. Para a função Notify Feasible só serão aceitos pacotes com a chave `notify-feasible-call` (tipo `string`).

- **payload**: Será um outro objeto JSON com o conteúdo da mensagem (tipo `dict`).

    - **date**: Data da infração no formato RFC 3339 (tipo `string`).

    - **id_radar**: Número de identificação do radar que capturou a infração (tipo `integer`).

    - **considered_speed**: Velocidade considerada na leitura da infração (tipo `integer`).

    - **vehicle_speed**: Velocidade medida pelo o equipamento na infração (tipo `string`).

    - **max_allowed_speed**: Velocidade máxima permitida pela via da infração (tipo `string`).

- **time**: O dia e horário em que essa mensagem foi enviado no formato RFC3339, ou seja, `YYYY-MM-DDTHH:MM:SSZ` (tipo `string`).

__Exemplo__:

```json
{
  "id":  "2387394a-bc7e-4dc9-8295-be8a619e5b5e",
  "payload": {
    "date":  "2019-06-07T19:24:04.102394Z",
    "id_radar": 2,
    "considered_speed": 57,
    "vehicle_speed": 64,
    "max_allowed_speed": 60
  },
  "time":  "2019-06-07T19:24:04.102394Z",
  "type":  "radar-infraction"
}
```

## Tecnologias Utilizadas

- Plataforma OpenFaaS
    - _Self-Hosted_ Function as a Service
- Python 3
- JSON

## Ambiente de Desenvolvimento

Recomendado o uso de OpenFaaS local em Docker Swarm.

O guia para criar o ambiente local está disponível [na seção de _Deployment_ da documentação do OpenFaaS](http://docs.openfaas.com/deployment/docker-swarm/).

Editor de texto de preferência.

## Ambiente de Teste Local

Recomendados a utilização de um ambiente virtual criado pelo módulo `virtualenvwrapper`.
Existe um sítio virtual com instruções em inglês para a instalação que pode ser acessado [aqui](https://virtualenvwrapper.readthedocs.io/en/latest/install.html). Mas você pode também seguir o roteiro abaixo para a instalação do ambiente:

```shell
python3 -m pip install -U pip # Faz a atualização do pip
python3 -m pip install virtualenvwrapper # Caso queira instalar apenas para o usuário use a opt --user
```

Agora configure o seu shell para utilizar o virtualenvwrapper, adicionando essas duas linhas ao arquivo de inicialização do seu shell (`.bashrc`, `.profile`, etc.)

```shell
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
```

Caso queira adicionar um local específico de projeto basta adicionar uma terceira linha com o seguinte `export`:

```shell
export PROJECT_HOME=/path/to/project
```

Execute o arquivo de inicialização do shell para que as mudanças surtam efeito, por exemplo:

```shell
source ~/.bashrc
```

Agora crie um ambiente virtual com o seguinte comando (colocando o nome que deseja para o ambiente), neste exemplo usarei o nome composta:

```shell
mkvirtualenv fn-notify-feasible
```

Para utilizá-lo:

```shell
workon fn-notify-feasible
pip install -r compiler/requirements.txt # Irá instalar todas as dependências usadas no projeto
```

**OBS**: Caso o sua variável de ambiente *PROJECT_HOME* esteja _setada_ ao executar o `workon` você será levado para o diretório lá configurado.

Para outras configurações e documentação adicional acesse a página do [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/).

## Deploy Local para Desenvolvimento

Para deploy da função, basta seguir o roteiro abaixo:

```shell
faas build -f fn-notify-feasible.yml
faas deploy -f fn-notify-feasible.yml
```

Para utilizá-lo, teste pela interface web no endereço definido, chamar pela CLI, ou por requisição HTTP:

FaaS CLI:

```shell
echo $'{\n  "id":  "2387394a-bc7e-4dc9-8295-be8a619e5b5e",\n  "payload": {\n    "date":  "2019-06-07T19:24:04.102394Z",\n    "id_radar": 2,\n    "infraction": 1,\n    "considered_speed": 82,\n    "vehicle_speed": 87,\n    "max_allowed_speed": 60\n  },\n  "time":  "2019-06-07T19:24:04.102394Z",\n  "type":  "radar-infraction"\n}' | faas-cli invoke fn-notify-feasible
```

HTTP-Request:

```shell
curl -d $'{\n  "id":  "2387394a-bc7e-4dc9-8295-be8a619e5b5e",\n  "payload": {\n    "date":  "2019-06-07T19:24:04.102394Z",\n    "id_radar": 2,\n    "infraction": 1,\n    "considered_speed": 82,\n    "vehicle_speed": 87,\n    "max_allowed_speed": 60\n  },\n  "time":  "2019-06-07T19:24:04.102394Z",\n  "type":  "radar-infraction"\n}' -X POST http://127.0.0.1:8080/function/fn-notify-feasible
```

Exemplo de saída:

```shell
{'status_code': 200, 'message': 'A probabilidade da infração 2387394a-bc7e-4dc9-8295-be8a619e5b5e (ID) ter se tornado um acidente foi de 69.58%. A notificação 2d8c3d23-efcd-499c-bf1c-11e061767675 foi enviada!'}
```

## Execução do Ambiente de Testes

Para executar os testes do fn-notify-feasible siga o roteiro descrito abaixo:

Primeiro assegure-se de que tem todas as dependências necessárias para executar o projeto.

```shell
pip install -r fn-notify-feasible/requirements.txt
# Ou caso não esteja trabalhando com uma virtualenv
python3 -m pip install -r fn-notify-feasible/requirements.txt
```

**OBS**: Caso queria instalar apenas para o usuário e não no sistema use a opt `--user` ao final do comando pip.

Agora que todas as dependências estão instaladas basta rodar o comando do pytest para verificar se o código está de acordo com o teste.

```shell
pytest fn-notify-feasible/ # Executa os testes no pytest
py.test --cov=fn-notify-feasible fn-notify-feasible/ # Executa os testes e avalia a cobertura estática de código
py.test --cov=fn-notify-feasible --cov-report html fn-notify-feasible/ # Faz o mesmo papel que o comando anterior, além de gerar uma pasta htmlcov/ com uma página relatório da cobertura
flake8 fn-notify-feasible/* # Executa o PEP8 linter nos arquivos python
```

Durante o `pytest` e o `py.test`, o terminal lhe apresentará um _output_ com o relatório dos testes e a cobertura de testes da aplicação. Para outras configuraões e documentação complementar acesse o sítio virtual do provedor do [pytest](https://docs.pytest.org/en/latest/) e do [coverage](https://pytest-cov.readthedocs.io/en/latest/).

Durante o `flake8`, o terminal lhe apresentará um relatório com os erros e _warnings_ do guia de estilo PEP8 do python, para demais configurações e documentações você pode acessar o sítio do [flake8](http://flake8.pycqa.org/en/latest/index.html) ou visualizar o estilo do [PEP8](https://www.python.org/dev/peps/pep-0008/).
