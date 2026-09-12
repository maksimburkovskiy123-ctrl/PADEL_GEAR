# Публикация на GitHub

В проект добавлен workflow `.github/workflows/tests.yml`. После каждого push или pull request GitHub будет автоматически устанавливать зависимости и запускать тесты.

## Первый push

После создания пустого репозитория на GitHub выполнить в корне проекта:

```bash
git init
git add .
git commit -m "Prepare padel racket recommendation MVP"
git branch -M main
git remote add origin https://github.com/<username>/<repository>.git
git push -u origin main
```

Вместо `<username>` и `<repository>` нужно указать данные созданного репозитория. Файлы базы SQLite, загруженные материалы и служебные файлы окружения исключены через `.gitignore`.

