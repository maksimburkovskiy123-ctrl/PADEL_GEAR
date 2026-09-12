# Проверка исходного каталога

Дата ручной проверки: **2026-09-12 UTC**. Цены ориентировочные, в валюте источника, без пересчета в рубли. Наличие ссылки и `verified=True` само по себе не доказывает правильность данных; ниже записано, что проверено.

| Модель | Текущая цена | Обычная цена при скидке | Источник |
| --- | --- | --- | --- |
| Babolat Counter Veron 2.6 | 260 USD | не показана | https://www.babolat.com/us/counter-veron-2.6/150181.html |
| Babolat Technical Viper 3.0 | 390 USD | не показана | https://www.babolat.com/us/technical-viper-3.0/150175.html |
| Babolat Counter Viper 2.6 | 340 USD | не показана | https://www.babolat.com/us/counter-viper-2.6/150177.html |
| Babolat Technical Veron 3.0 | 240 USD | не показана | https://www.babolat.com/us/technical-veron-3.0/150183.html |
| Babolat Counter Vertuo 2.6 | 200 USD | не показана | https://www.babolat.com/us/counter-vertuo-2.6/150185.html |
| Babolat Air Origin | 140 USD | не показана | https://www.babolat.com/us/air-origin/150153.html |
| Babolat Counter Origin | 120 USD | не показана | https://www.babolat.com/us/counter-origin/150154.html |
| Bullpadel Xplo PP26 | 379.99 EUR | не показана | https://www.bullpadel.com/gb/5951-pala-bullpadel-xplo-pp26.html |
| Bullpadel Wonder (2026) | 199.98 EUR | 269.99 EUR | https://www.bullpadel.com/gb/5689-racket-bullpadel-wonder.html |
| Bullpadel Neuron 02 Edge (2026) | 239.99 EUR | 319.99 EUR | https://www.bullpadel.com/gb/5685-racket-bullpadel-neuron-02-edge.html |
| Bullpadel Icon 26 | 209.99 EUR | 279.99 EUR | https://www.bullpadel.com/gb/5686-racket-bullpadel-icon-26.html |
| Bullpadel Pearl 26 | 209.99 EUR | 279.99 EUR | https://www.bullpadel.com/gb/5625-bullpadel-racket-pearl-26.html |
| Adidas Arrow Hit (2026) | **400 EUR** | не показана | https://allforpadel.com/en/padel-rackets/7523-padel-racket-adidas-arrow-hit-8435739405888.html |
| Adidas Arrow Hit CTRL (2026) | **400 EUR** | не показана | https://allforpadel.com/en/padel-rackets/7526-padel-racket-adidas-arrow-hit-ctrl-8435739405895.html |
| Adidas Match Black 2026 | **75 EUR** | не показана | https://allforpadel.com/en/padel-rackets/7493-padel-racket-adidas-match-black-2026-8435739406052.html |

## Основания проверки

- Babolat: цена в `.m-product-detail__prices .c-price__value`, проверена по Product JSON-LD с валютой USD и соответствующим товаром.
- Bullpadel: блок `.product__prices` возле основного заголовка, отдельно `Price` и `Regular price`; offers у соответствующего Product подтверждают EUR.
- Adidas: основной блок `.product_header_container .product-prices`, `itemprop="price"` и артикулы: Arrow Hit `AR1AB0U30` (400), CTRL `AR1CB1U23` (400), Match `AR5GA3U23` (75), EUR, налог включен.
- Старые 160 EUR для Arrow Hit относились к обуви Crazyquick Boost M; 234 EUR у Match относились к Metalbone HRD+ 3.4. Происхождение старых 168 EUR для CTRL не установлено. Все три цены исправлены. Это разовое исправление, автоматического обновления цен нет.
- Исходные вес и баланс всех 15 записей совпали со спецификациями. У Neuron точная форма `Geometric / Diamond`, в фильтрах она нормализована до `geometric`.
- У Wonder и Pearl указаны Professional и Advanced. Каталог хранит одну категорию `professional`; при подборе для advanced это соседний уровень, не полное совпадение.
- В описаниях Air Origin и Counter Origin говорится о первых шагах/первых матчах. Формальное поле уровня не найдено, поэтому `unknown` сохранен. У остальных пяти Babolat точная категория тоже не подтверждена.
- Год коллекции Adidas и Bullpadel подтвержден текстом страниц. У Babolat годы в именах файлов изображений не использованы как доказательство года выпуска; ориентиром служит точная версия и product ID.

## Нормализация и границы

- Вес: номинал Babolat или середина указанного производителем диапазона. Фильтр: `light <= 355`, `355 < medium <= 370`, `heavy > 370` г. Это категории приложения, не обещание веса каждого экземпляра.
- Числовой баланс: `low <= 260`, `260 < even < 270`, `high >= 270` мм. Словесные Head Heavy / Slightly Head Heavy -> high; Even -> even. Это грубые группы для учебного алгоритма, а не универсальная классификация брендов.
- Counter Striker -> control, Technical Striker / Offensive / Attack -> power, Versatile -> balanced. Air Origin отнесен к balanced по описанию универсальности. Это интерпретация назначения, не измеренные оценки контроля или мощности.
- `verified` относится к ручной проверке исходного каталога. Новые записи по умолчанию не проверены. При ручном изменении характеристик нужно обновить основания проверки и этот журнал.

## Найденные фотографии для будущих референсов

Это официальные фотографии, **не 3D-файлы**. Конкретные модели для 3D еще должен выбрать пользователь. Для похожей модели потребуются вид спереди, сзади, сбоку и проверка пропорций. Неизвестные размеры не следует выдавать за заводские.

- Adidas Arrow Hit 2026: https://allforpadel.com/9099-thickbox_default/padel-racket-adidas-arrow-hit.jpg
- Babolat Technical Viper 3.0: https://media.babolat.com/image/upload/f_auto,q_auto,c_pad,w_3024,h_3024/v1741095799/Product_Media/2026/Padel/RACQUETS/150175-TECHNICAL_VIPER_3.0-100-1-Face.png
- Bullpadel Pearl 26: https://www.bullpadel.com/18915-product_main_2x/bullpadel-racket-pearl-26.jpg

Фотографии пока не скачаны и не включены в приложение. Перед публикацией текстур нужно проверить условия их использования.
