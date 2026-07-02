# Задание для Manus — поднять CPU-ноду прувера (Layer 2) для secp256k1/ECDLP

Ты — автономный агент с доступом к Hetzner API. Задача: одноразово поднять и запустить
**CPU-сервер как ноду автономного прувера** для репозитория
`KeyAIGit/-ecdlp-lean-verification`. Вся инфраструктура уже в репо — тебе нужно
провиженить машину, прогнать готовый setup, положить секреты и запустить демон.

Отчитайся строго по «Критериям приёмки». **Никаких секретов в чат, в репозиторий или в
логи.**

---

## 0. Безопасность (сделать ПЕРВЫМ, до всего)
1. **Ротировать Hetzner API-токен.** Старый токен считай скомпрометированным (был засвечен
   в переписке). Hetzner Console → Security → API Tokens → удалить старый → создать новый.
   Работай под новым. Нигде его не публикуй.
2. **Старый root-пароль скомпрометирован.** На новой машине — только вход по SSH-ключу,
   парольный вход отключить (`PasswordAuthentication no`).
3. Секреты (Featherless key, GitHub PAT) живут **только** файлами `0600` на сервере, не в
   git, не в echo, не в истории shell (`set +o history` перед вводом или `read -rs`).
4. TLS не отключать.

## 1. Провижн сервера
- Провайдер: Hetzner Cloud. Если рабочая нода уже существует — переиспользуй её (сначала
  проверь, что на ней нет чужих/неизвестных процессов; если сомнение — подними чистую).
- Тип: **CPU, ≥ 4 vCPU / ≥ 8 GB RAM / ≥ 80 GB диск** (кэш Mathlib ~6–8 GB oleans + сборка).
  Подойдёт напр. `CPX31` или `CCX23`. **GPU не нужен** — модели прувера в облаке Featherless,
  сервер их только вызывает и быстро валидирует ответ.
- ОС: **Ubuntu 24.04**.
- Создай свежий SSH-ключ для доступа, приватную часть держи у себя, не коммить.

## 2. Установка (готовый скрипт, ~10–15 мин)
```bash
apt-get update -y && apt-get install -y git tmux curl
cd /root
git clone https://github.com/KeyAIGit/-ecdlp-lean-verification.git
cd -ecdlp-lean-verification
bash scripts/server-setup.sh                         # Lean v4.31.0 + Mathlib cache + build
~/.elan/bin/lake env lean Ecdlp/Proved/CubeRoot.lean && echo "LEAN OK"   # sanity-check
```
`LEAN OK` без ошибок = тулчейн и кэш рабочие.

## 3. Секреты (ввод без эха, файлы 0600)
```bash
read -rsp "Featherless API key: " FK; echo; printf '%s' "$FK" > ~/.featherless_key; chmod 600 ~/.featherless_key; unset FK
read -rsp "GitHub PAT: " PAT; echo
git config --global credential.helper store
printf 'https://x-access-token:%s@github.com\n' "$PAT" > ~/.git-credentials; chmod 600 ~/.git-credentials; unset PAT
```
- **GitHub PAT:** fine-grained token, доступ **только** к `KeyAIGit/-ecdlp-lean-verification`,
  права **Contents: Read and write** (и ничего больше). Срок 30–90 дней. Демону этого хватает,
  чтобы пушить ветку `server/candidates`.
- **Featherless key:** ключ плана, где доступны `Pythagoras-Prover-4B` и `Goedel-Prover-V2-32B`.

## 4. Запуск демона
```bash
tmux new -d -s prover 'bash scripts/prover_daemon.sh >> ~/prover-daemon.log 2>&1'
tail -f ~/prover-daemon.log     # первые строки должны показать: kickstart, warm Lean, цикл по targets/
```
Опционально надёжнее — обернуть в `systemd`-юнит (`Restart=always`), чтобы переживал ребут;
`scripts/prover_daemon.sh` для этого пригоден.

## Что нода делает (честный scope)
- **Тёплая верификация:** `lake env lean` ~30 с против ~5 мин на CI → цикл прувера ~10× быстрее,
  работает 24/7.
- Гоняет **Tier-0 лестницу тактик** (`rfl/decide/native_decide/simp/omega/ring/aesop`), затем
  Featherless-модели, передавая им точную ошибку Lean.
- Кернел-принятые кандидаты пушит в ветку **`server/candidates`** (НИКОГДА не в `main` и не в
  `Ecdlp/Proved/` напрямую). Промоушен в базу — отдельным ревью-PR, мержит человек.
- **Ограничение честно:** Tier-0 закрывает конкретные/разрешимые цели; структурные глубокие
  теоремы всё равно требуют формализации ассистентом/человеком. Нода расширяет *широту*
  графа и снимает механический перебор — это не шорткат к глубоким результатам.

## Критерии приёмки (что прислать в отчёте — без секретов)
1. Тип и регион сервера, vCPU/RAM/диск (без IP, если можно — или IP отдельным приватным каналом).
2. Вывод `LEAN OK` из шага 2.
3. Подтверждение, что оба секрет-файла существуют с правами `0600` (например `ls -l ~/.featherless_key ~/.git-credentials` — только права и путь, не содержимое).
4. Что демон запущен: имя tmux-сессии / PID и **последние 20 строк** `~/prover-daemon.log`
   (убедись, что там нет ключей — скрипт их не печатает, но проверь).
5. Появилась ли ветка `server/candidates` в GitHub (может быть пусто, если Tier-0 пока ничего не
   закрыл — это нормально, это диагностика, а не провал).
6. Подтверждение, что старый Hetzner-токен удалён и парольный SSH отключён.

## Чего НЕ делать
- Не трогать `main` и `Ecdlp/Proved/` прямыми пушами.
- Не коммитить и не печатать ключи/токены/приватные ключи/IP в публичные места.
- Не ставить GPU/тяжёлые CAS без запроса (можно `WITH_CAS=1 bash scripts/server-setup.sh`
  для PARI/sympy, если понадобится числовой скрэтчпад — по желанию).
