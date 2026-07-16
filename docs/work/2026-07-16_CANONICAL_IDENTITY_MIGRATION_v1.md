# ARTEMIS Canonical Identity Migration v1

## Статус

- Issue: `#281`.
- Статус: completed.
- Дата фиксации snapshot: 2026-07-16.
- Дата применения и проверки: 2026-07-16.
- Source: Airtable `Artemis_Base / Features` + checked-in `data/features.json`.
- Scope: заменить 11 невалидных business ID, отделить Airtable `rec...` от public identity и сохранить обратную совместимость Research Slices.

## Инварианты

1. `Features.id` — единственный canonical public ID, UUID v4.
2. Airtable record ID хранится как `source_record_id` и никогда не публикуется как `Feature.id`.
3. Старые ссылки разрешаются только через versioned `data/id_aliases.json` и `properties.legacy_ids`.
4. Канонический ID после migration не изменяется вручную.
5. ETL, release gate и moderation publish блокируют отсутствующий, не-v4 или дублирующийся ID.

## Зафиксированная таблица замены

| Airtable record | Объект | Старый business ID | Новый canonical UUID v4 |
|---|---|---|---|
| `rec0x9MvhXQFWErOy` | Бурдж-Халифа | `x1y2z3a4-1122-4b9a-8c7d-6e5f4a3b2c1d` | `7f52d67f-ea2b-4c40-aec0-9aef0597dddb` |
| `recIO5H5Vqw2xwfLq` | Версальский дворец | `g1a2u3d4-1904-4b9a-8c7d-6e5f4a3b2c1d` | `bcd1bc1c-1093-430c-ae75-a0da6c06524d` |
| `rec1GDGqssFGehzEx` | Вилла Савой | `h1i2t3e4-1971-4b9a-8c7d-6e5f4a3b2c1d` | `1f49bb51-07a2-4c86-8101-edb6e525503e` |
| `recV3Kj5ounTF55mw` | Еврейский музей | `s1a2m3p4-5566-4b9a-8c7d-6e5f4a3b2c1d` | `f3c73867-e20a-457b-a974-7e8478ac0431` |
| `recmLwS8nYaR2dYEF` | Каса-Батльо | `m1o2d3e4-1929-4b9a-8c7d-6e5f4a3b2c1d` | `b1f1e062-b520-4894-a364-444346c9ef1c` |
| `recr1NbkVTbJwP5Ia` | Королевский национальный театр | `d1e2c3o4-1992-4b9a-8c7d-6e5f4a3b2c1d` | `71ab11dd-f159-43d3-bcf9-711380973f0e` |
| `recHqE46e2W3EDBlO` | Крайслер-билдинг | `b7r8u9t0-1963-4b9a-8c7d-6e5f4a3b2c1d` | `c4acd963-5446-409f-82af-a495ed4a39d4` |
| `recAJJSQH0dvmnpp0` | Пантеон (Париж) | `a1r2d3e4-1928-4b9a-8c7d-6e5f4a3b2c1d` | `acfb7492-c49d-4e71-9bbc-bd446b52d32d` |
| `rec7xto7TNSberKPg` | Собор Святого Петра | `p1a2n3t4-1758-4b9a-8c7d-6e5f4a3b2c1d` | `393c7d17-d266-4e8b-8412-b96eb427f941` |
| `rec9KIQPB9M377wgE` | Центр Жоржа Помпиду | `n1e2o3f4-2004-4b9a-8c7d-6e5f4a3b2c1d` | `70c2ee8e-4016-46d4-be32-11d3ac7d9726` |
| `rec8RKV55zHUCA4bc` | Шартрский собор | `v1e2r3s4-1661-4b7a-9c2d-8e6f5a4b3c2d` | `dc4b7dde-e7b6-4a71-8bf2-0b7056266635` |

Оставшиеся 8 Features уже имели валидные UUID v4 и сохраняют их без изменений. Их `rec...` идентификаторы также входят в alias map для восстановления ранее сохранённых ссылок.

## Порядок выполнения

1. Зафиксировать snapshot и alias map в Git.
2. Перевести ETL, import/export, moderation publish и release gate на `Features.id`.
3. Добавить frontend resolution старых Slice/Story IDs через `legacy_ids`.
4. Прогнать unit, integration, dry-run и release checks.
5. Одним batch update заменить ровно 11 значений Airtable `Features.id`.
6. Повторно прочитать эти 11 records и подтвердить `id_status=ok`.
7. Опубликовать draft PR; после merge запустить canonical Airtable export.

## Recovery

- Airtable record IDs не меняются, поэтому каждая строка однозначно восстанавливается по этому документу.
- Старые business ID не удаляются из истории: они остаются ключами `data/id_aliases.json`.
- При ошибке до merge branch не публикуется; Airtable values можно точечно вернуть по колонке «Старый business ID».
- После merge откат public artifacts допускается только вместе с сохранением alias map, чтобы не ломать уже созданные canonical ссылки.

## Execution evidence

- 11 Airtable `Features.id` обновлены по таблице выше без изменения record IDs или других полей.
- Batch выполнен безопасно в два шага: 1 record для write/формулы smoke check, затем оставшиеся 10 records.
- Немедленный ответ Airtable после каждого шага вернул `id_status=ok`.
- Контрольное чтение всей таблицы Features: `19 total / 19 id_status=ok / 0 invalid`.
- Checked-in `data/features.json`, `data/features.geojson` и `data/id_aliases.json` содержат те же 19 canonical UUID.
- Реализация и CI evidence: draft PR `#290`; четыре PR workflow завершились `success`.
