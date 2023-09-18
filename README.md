# django_sprint4
Подготовка к выполнению задания:
1. Клонируйте репозиторий django_sprint4 на свой компьютер, в рабочую папку Dev/.
2. Скопируйте выполненное домашнее задание прошлого спринта из директории django_sprint3/blogicum/ в папку django_sprint4/blogicum/.
3. Разверните и активируйте виртуальное окружение в папке Dev/django_sprint4/, установите в него зависимости из requirements.txt.
4. После установки проекта должна получиться такая структура файлов:

Dev/
 └── django_sprint4/
     ├── .github/    Служебная папка с настройками репозитория (скрытая)   
     ├── .vscode/    Служебная папка редактора кода (опционально, скрытая)
     ├── .git/       Служебная информация Git (скрытая)
     ├── tests/             Тесты Практикума, проверяющие проект
     ├── venv/              Директория виртуального окружения
     ├── blogicum/          <-- Директория проекта
     |   ├── blog/
     |   ├── pages/
     |   ├── static/
     |   ├── templates/     <-- Перенесите новые шаблоны сюда 
     |   ├── blogicum/
     |   ├── db.sqlite3     Файл базы данных (может и не быть)
     |   └── manage.py      
     ├── .gitignore         Список файлов и папок, скрытых от отслеживания Git (скрытый) 
     ├── db.json            <-- Фикстуры для базы данных    
     ├── LICENSE            Лицензия   
     ├── pytest.ini         Конфигурация тестов Практикума
     ├── README.md          Описание проекта 
     ├── requirements.txt   Список зависимостей проекта
     └── setup.cfg          Настройки тестов Практикума 

Дополнительные материалы
Для финальной версии проекта мы подготовили новую версию шаблонов всех страниц. Они уже свёрстаны и разложены по приложениям и директориям. В нужных местах уже указаны соответствующие переменные контекста — они помогут вам выполнить задание. Скачать шаблоны можно по ссылке.
https://code.s3.yandex.net/backend-developer/learning-materials/templates/templates.zip

Задание
Вот перечень задач, которые вам нужно выполнить:


Кастомные страницы для ошибок.
Подключите к проекту и настройте кастомные страницы для ошибок 403 CSRF, 404 и 500. Шаблоны для этих страниц находятся в директории templates/pages/.


Работа с пользователями.
Подключите к проекту пользователей:
Подключите к проекту пути для работы с пользователями из django.contrib.auth.urls.
Переопределите шаблоны для каждой подключённой страницы.
Создайте страницу auth/registration/ с формой для регистрации пользователей.
Создайте страницу пользователя profile/<username>/. На ней должны отображаться:
a. информация о пользователе (доступна всем посетителям),
b. публикации пользователя (доступны всем посетителям),
c. ссылка на страницу редактирования профиля для изменения имени, фамилии, логина и адреса электронной почты (доступна только залогиненному пользователю — хозяину аккаунта),
d. ссылка на страницу изменения пароля (доступна только залогиненному пользователю — хозяину аккаунта).
Переопределять встроенную модель пользователя не требуется.


Пагинация.
Подключите к проекту пагинацию и настройте вывод не более 10 публикаций
на главную страницу,
на страницу пользователя,
на страницу категории.


Изображения к постам.
Добавьте возможность прикреплять изображение к публикациям проекта. Если изображение добавлено, то оно должно отображаться в публикациях на
главной странице,
странице пользователя,
странице категории,
отдельной странице публикации.


Добавление новых публикаций.
У зарегистрированных пользователей должна быть возможность самостоятельно публиковать посты. Создайте страницу для публикации новых записей posts/create/:
Страница добавления публикации должна быть доступна только авторизованным пользователям.
После валидации формы и добавления новой публикации пользователь должен быть перенаправлен на свою страницу profile/<username>/.
Новые категории и местоположения может создавать только администратор сайта через панель администратора.
Указав дату публикации «в будущем», можно создавать отложенные посты. Они должны стать доступны всем посетителям с момента, указанного в поле «Дата». Отложенные публикации должны быть доступны автору сразу же после отправки; автор должен видеть на своей странице все свои публикации, включая отложенные и снятые с публикации администратором.


Редактирование публикаций.
Добавьте страницу редактирования публикации с адресом posts/<post_id>/edit/.
Права на редактирование должны быть только у автора публикации. Остальные пользователи должны перенаправляться на страницу просмотра поста.
Для страницы редактирования поста должен применяться тот же HTML-шаблон, что и для страницы создания нового поста: blog/create_post.html.
После окончания редактирования пользователь должен переадресовываться на страницу отредактированной публикации.


Комментарии к публикациям.
Создайте систему комментирования записей. На странице поста под текстом записи должна выводиться форма для отправки комментария, а ниже — список комментариев.
Комментарии должны быть отсортированы по времени их публикации, «от старых к новым».
Комментировать публикации могут только авторизованные пользователи.
Авторы комментариев должны иметь возможность отредактировать собственные комментарии.
Для каждой публикации на
главной странице,
странице пользователя,
странице категории
нужно выводить количество комментариев.
Адрес для добавления комментария posts/<post_id>/comment/
Адрес для редактирования комментария posts/<post_id>/edit_comment/<comment_id>/


Удаление публикаций и комментариев.
Авторизованные пользователи должны иметь возможность удалять собственные публикации и комментарии. Перед удалением материала должна открываться подтверждающая страница, содержащая публикацию или комментарий. Для подтверждающей страницы не надо создавать отдельные шаблоны; для этого необходимо переиспользовать существующие шаблоны, необходимая логика в них уже присутствует.
Адрес для удаления публикации posts/<post_id>/delete/
Адрес для удаления комментария posts/<post_id>/delete_comment/<comment_id>/


Новые статичные страницы.
Обновите механизм создания и изменения статичных страниц в проекте, используя CBV. Адреса уже существующих статичных страниц не должны измениться.


Отправка электронной почты.
Подключать к проекту реальный почтовый сервер сейчас нет необходимости, поэтому подключите файловый бэкенд: все «отправленные» письма должны аккумулироваться в специальной директории проекта sent_emails/. 

Проверка
После выполнения задания: 
Запустите тесты локально, на компьютере. В активированном виртуальном окружении через терминал из папки Dev/django_sprint4 выполните команду pytest.
Если все тесты пройдены успешно — значит, проект готов к отправке на GitHub.