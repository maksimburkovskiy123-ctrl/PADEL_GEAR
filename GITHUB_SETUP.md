# Публикация на GitHub

В проект добавлен workflow `.github/workflows/tests.yml`. После каждого push или pull request GitHub будет автоматически устанавливать зависимости и запускать тесты.

## Обновление репозитория

Репозиторий уже создан: `https://github.com/maksimburkovskiy123-ctrl/PADEL_GEAR`.
После изменений выполнить в корне проекта:

```bash
git add .
git commit -m "Finish MVP and add teacher launch scripts"
git push origin main
```

Для push нужен вход в GitHub под аккаунтом с правом записи в репозиторий. Файлы базы SQLite, локальное окружение и служебные файлы исключены через `.gitignore`.
