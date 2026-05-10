# httpstat-docker-ansible

Практическое решение задания на Python, Docker и Ansible.

## Структура

- `script/main.py` - Python-скрипт для запросов к `https://httpstat.us`
- `requirements.txt` - зависимости для Python-скрипта
- `docker/Dockerfile` - Docker-образ на базе `ubuntu:22.04`
- `ansible/inventory.ini` - inventory для локального запуска
- `ansible/playbook.yml` - playbook для установки Docker, сборки образа и проверки контейнера

## Требования

- Python 3.10+
- Docker
- Ansible 2.14+

## Раздел 1. Запуск скрипта

Установить зависимости:

```bash
pip install -r requirements.txt
```

Запустить скрипт:

```bash
python3 script/main.py
```

Скрипт выполняет 5 запросов и логирует результат в консоль. Для `4xx` и `5xx` он завершает работу с кодом `1`.

## Раздел 2. Docker

Собирать образ нужно из корня репозитория:

```bash
docker build -t httpstat-script -f docker/Dockerfile .
```

Запустить контейнер:

```bash
docker run --rm httpstat-script
```

Если нужен фоновой запуск и просмотр логов:

```bash
docker run -d --name httpstat-test httpstat-script
docker logs -f httpstat-test
```

## Раздел 3. Ansible

Playbook работает локально и делает следующее:

- устанавливает Docker
- добавляет текущего пользователя в группу `docker`
- запускает и включает `docker.service`
- собирает Docker-образ
- запускает контейнер
- проверяет код завершения
- выводит логи контейнера

Запуск из каталога `ansible`:

```bash
cd ansible
ansible-playbook -i inventory.ini playbook.yml
```

## Примечание

В репозитории используется `localhost` через `ansible_connection=local`, поэтому playbook можно выполнять без удалённого хоста.
Чтобы переключиться на определнный хост - изменить закомментированнуб строку в inventory.ini на данные целового хоста.