const I18N_STORAGE_KEY = "ds131-lang";

const STRINGS = {
  ru: {
    "brand.tag": "Синтетические табличные данные",
    "brand.aria": "DataSynthesis131 — на главную",
    "nav.about": "О платформе",
    "nav.home": "Главная",
    "lang.menu": "Выбор языка",
    "lang.ru": "Русский",
    "lang.en": "English",

    "step.upload": "1. Загрузка данных",
    "step.preview": "2. Превью датасета",
    "step.params": "3. Параметры генерации",
    "step.progress": "4. Генерация",
    "step.results": "5. Результаты",

    "tab.file": "Файл (CSV / Excel)",
    "tab.kaggle": "Kaggle URL",
    "upload.drop": "Перетащите CSV / XLS файл или нажмите для выбора",
    "kaggle.url": "Ссылка на датасет Kaggle",
    "kaggle.file": "Имя CSV-файла (необязательно)",
    "kaggle.custom": "Свои Kaggle credentials",
    "kaggle.username": "Kaggle username",
    "kaggle.key": "Kaggle API key",
    "kaggle.save": "Запомнить на этом устройстве",
    "kaggle.btn": "Загрузить с Kaggle",

    "stat.rows": "Строк",
    "stat.cols": "Колонок",
    "stat.file": "Файл",
    "preview.caption": "Показаны первые {shown} из {total} строк",

    "field.numRows": "Число строк",
    "field.target": "Целевая переменная",
    "field.target.hint": "Если не выбрана, используется auto target (cluster)",
    "target.auto": "Авто (cluster)",
    "field.method": "Метод генерации",
    "method.auto": "Авто — по типу датасета",
    "method.gc": "Gaussian Copula",
    "method.ctgan": "Conditional GAN",
    "method.cgan": "Copula GAN",
    "method.tvae": "Tabular VAE",
    "method.tip.btn": "Подробности по моделям",
    "method.tip.link": "О моделях генерации",

    "field.epochs": "Epochs",
    "field.epochs.hint": "100–1000",
    "toggle.fast": "Быстрый результат",
    "toggle.fast.desc": "Фиксирует Gaussian Copula",
    "toggle.missing": "Сохранять пропуски",
    "toggle.missing.desc": "Иначе NaN заполняются автоматически",
    "toggle.merge": "Объединить с входным датасетом",
    "toggle.merge.desc": "В итоговый CSV попадут real + synthetic",

    "btn.generate": "Сгенерировать",
    "btn.download.csv": "Скачать CSV",
    "btn.download.xlsx": "Скачать Excel",
    "btn.download.pdf": "Скачать PDF-отчёт",
    "results.plots": "Визуализация датасета",
    "progress.wait": "Ожидание...",

    "analysis.title": "Анализ датасета:",
    "analysis.type": "Тип",
    "analysis.balance": "Баланс",
    "analysis.recommended": "Рекомендуемый метод",

    "metric.propensity": "Propensity score (↓ лучше)",
    "metric.logcluster": "Log-cluster (↓ лучше)",
    "metric.accuracy": "Prediction accuracy (↑ лучше)",
    "metric.sdv": "SDV score",
    "metric.validity": "Data validity",
    "metric.method": "Метод генерации",
    "metric.overall": "Общая оценка качества",
    "metric.overall.about": "Как считается? → QualityEvaluator",

    "plots.tab.sdv": "Распределения",
    "plots.tab.corr": "Корреляции",
    "plots.explore": "Исследовать колонку",
    "plots.select.placeholder": "— выбрать колонку —",

    "status.uploading": "Загрузка файла...",
    "status.uploaded": "Датасет загружен",
    "status.kaggle.missing": "Укажите ссылку на Kaggle",
    "status.kaggle.loading": "Загрузка с Kaggle (может занять время)...",
    "status.upload.error": "Ошибка загрузки",
    "status.kaggle.error": "Ошибка Kaggle",
    "status.gen.start": "Запуск генерации...",
    "status.gen.fail": "Не удалось запустить",
    "error.unknown": "Неизвестная ошибка",
    "error.pandas":
      "Ошибка обработки таблицы (pandas): несовпадение колонок при заполнении пропусков.",

    "about.title": "О платформе",
    "about.platform.title": "Платформа",
    "about.platform.lead":
      'Веб-сервис для генерации табличных данных на основе входного датасета. Ключевая особенность: платформа автоматически выбирает наиболее подходящий метод генерации по характеристикам входного датасета. Проект основан на библиотеке <a href="https://github.com/MaratElagin/DataSynthesis131/tree/main/DataSynthesis131" target="_blank" rel="noopener">DataSynthesis131</a>. Итоговая квалификационная работа: <a href="https://kai.ru/structure/general/institutes/institute-of-technical-cybernetics-and-informatics/" target="_blank" rel="noopener">ИКТЗИ (КАИ)</a>, <a href="https://kpfu.ru/itis" target="_blank" rel="noopener">ИТИС (КФУ)</a>.',
    "about.platform.body2":
      "Пайплайн платформы повторяет практический сценарий: загрузка исходного датасета, анализ структуры, запуск синтеза с авто- или ручным выбором модели, оценка качества и выгрузка итогового CSV.",
    "about.platform.caption": "Верхнеуровневая архитектура платформы",
    "about.arch.alt": "Архитектурная схема платформы",
    "about.platform.flow.alt": "Основной workflow платформы",
    "about.platform.flow.caption": "Основной workflow библиотеки и платформы",
    "about.synth.title": "Synthesizer — как выбираем наиболее подходящий метод",
    "about.synth.body":
      "Synthesizer анализирует баланс классов, типы признаков, размер датасета и ограничения по скорости, после чего выбирает метод: Gaussian Copula, CTGAN, Copula GAN или TVAE.",
    "about.synth.body2":
      "При необходимости пользователь может зафиксировать конкретный метод вручную, а для нейросетевых моделей управлять качеством/скоростью через число эпох.",
    "about.synth.alg.alt": "Алгоритм выбора метода генерации",
    "about.synth.alg.caption": "Алгоритм автоматического выбора метода генерации",
    "about.methods.title": "Модели генерации",
    "about.methods.body":
      "Ниже краткое описание каждого метода генерации, который используется в платформе.",
    "about.methods.body2":
      "Ссылки ведут на документацию SDV по соответствующим синтезаторам.",
    "about.methods.gc":
      '<strong><a href="https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer" target="_blank" rel="noopener">Gaussian Copula</a></strong> — быстрый статистический метод, удобен для табличных данных с преобладанием числовых признаков.',
    "about.methods.ctgan":
      '<strong><a href="https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer" target="_blank" rel="noopener">CTGAN</a></strong> — нейросетевой метод для сложных зависимостей и условных распределений.',
    "about.methods.cgan":
      '<strong><a href="https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer" target="_blank" rel="noopener">Copula GAN</a></strong> — гибрид copula и GAN, часто полезен для небольших выборок.',
    "about.methods.tvae":
      '<strong><a href="https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer" target="_blank" rel="noopener">TVAE</a></strong> — вариационный автоэнкодер для смешанных числовых и категориальных признаков.',
    "about.methods.auto":
      "<strong>Auto</strong> — эвристика библиотеки выбирает метод по типу данных, балансу классов, размеру датасета и ограничениям по скорости.",
    "about.methods.map.alt": "Карта компонентов библиотеки",
    "about.methods.map.caption": "Связь компонентов и режимов генерации",
    "about.qe.title": "QualityEvaluator — как оцениваем качество сгенерированного датасета",
    "about.qe.body":
      "QualityEvaluator сравнивает real и synthetic по fidelity-метрикам: propensity score, log-cluster и prediction accuracy.",
    "about.qe.body2":
      "Оценка строится на наборе fidelity-метрик и дополнительных отчетах, которые показывают близость synthetic-данных к исходному датасету.",
    "about.qe.metrics.lead": "Ключевые метрики, используемые в платформе:",
    "about.qe.metric.prop":
      '<strong>Propensity score (pMSE)</strong> — оценивает, насколько легко отличить real от synthetic; чем ниже значение, тем лучше <a href="https://www.mdpi.com/2227-7390/11/15/3278" target="_blank" rel="noopener">(источник)</a>.',
    "about.qe.metric.log":
      '<strong>Log-cluster metric</strong> — измеряет разделимость real/synthetic в кластерах <a href="https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-020-00977-1" target="_blank" rel="noopener">(источник)</a>.',
    "about.qe.metric.pred":
      "<strong>Prediction accuracy</strong> — качество модели, обученной на synthetic и проверенной на real target.",
    "about.qe.metric.sdv":
      '<strong>SDMetrics / Data validity / SDV score</strong> — дополнительная проверка статистической согласованности и корректности синтетических данных <a href="https://docs.sdv.dev/sdmetrics" target="_blank" rel="noopener">(документация)</a>.',
    "about.qe.dist.alt": "Сравнение распределений real и synthetic",
    "about.qe.dist.caption": "Пример совпадения распределений real/synthetic",
    "about.qe.table.alt": "Отчет TableEvaluator",
    "about.qe.table.caption": "Фрагмент отчета TableEvaluator",
    "about.results.title": "Результаты измерений",
    "about.results.body":
      "В исследовании проведено сравнение моделей на датасетах разных типов: numerical / categorical / mixed, а также на выборках с разным балансом классов.",
    "about.results.body2":
      "Это позволяет оценить не только среднее качество, но и устойчивость методов в разных практических сценариях.",
    "about.results.chart.alt": "График сравнения моделей",
    "about.results.chart.caption": "Пример сравнения моделей на наборе слабосбалансированных числовых данных",
    "about.results.link": "Таблица результатов (Google Sheets)",
    "about.refs.title": "Исследования и ссылки",
    "about.refs.readme": "README библиотеки",
    "about.refs.colab": "Google Colab",
    "about.refs.video": "Видео-демо",
    "about.refs.notion": "Документация (Notion)",

    "footer.api": "REST API",
    "footer.issues": "Issues",
    "footer.telegram": "Telegram",
  },
  en: {
    "brand.tag": "Synthetic tabular data",
    "brand.aria": "DataSynthesis131 — home",
    "nav.about": "About platform",
    "nav.home": "Home",
    "lang.menu": "Language",
    "lang.ru": "Русский",
    "lang.en": "English",

    "step.upload": "1. Upload data",
    "step.preview": "2. Dataset preview",
    "step.params": "3. Generation parameters",
    "step.progress": "4. Generation",
    "step.results": "5. Results",

    "tab.file": "File (CSV / Excel)",
    "tab.kaggle": "Kaggle URL",
    "upload.drop": "Drag & drop a CSV / XLS file or click to choose",
    "kaggle.url": "Kaggle dataset URL",
    "kaggle.file": "CSV file name (optional)",
    "kaggle.custom": "Custom Kaggle credentials",
    "kaggle.username": "Kaggle username",
    "kaggle.key": "Kaggle API key",
    "kaggle.save": "Remember on this device",
    "kaggle.btn": "Download from Kaggle",

    "stat.rows": "Rows",
    "stat.cols": "Columns",
    "stat.file": "File",
    "preview.caption": "Showing first {shown} of {total} rows",

    "field.numRows": "Number of rows",
    "field.target": "Target variable",
    "field.target.hint": "If not selected, auto target (cluster) is used",
    "target.auto": "Auto (cluster)",
    "field.method": "Generation method",
    "method.auto": "Auto — by dataset type",
    "method.gc": "Gaussian Copula",
    "method.ctgan": "Conditional GAN",
    "method.cgan": "Copula GAN",
    "method.tvae": "Tabular VAE",
    "method.tip.btn": "Generation model details",
    "method.tip.link": "Details in generation models",

    "field.epochs": "Epochs",
    "field.epochs.hint": "100–1000",
    "toggle.fast": "Fast result",
    "toggle.fast.desc": "Locks Gaussian Copula",
    "toggle.missing": "Keep missing values",
    "toggle.missing.desc": "Otherwise NaNs are imputed automatically",
    "toggle.merge": "Merge with input dataset",
    "toggle.merge.desc": "Final CSV includes real + synthetic rows",

    "btn.generate": "Generate",
    "btn.download.csv": "Download CSV",
    "btn.download.xlsx": "Download Excel",
    "btn.download.pdf": "Download PDF Report",
    "results.plots": "Dataset visualization",
    "progress.wait": "Waiting...",

    "analysis.title": "Dataset analysis:",
    "analysis.type": "Type",
    "analysis.balance": "Balance",
    "analysis.recommended": "Recommended method",

    "metric.propensity": "Propensity score (↓ better)",
    "metric.logcluster": "Log-cluster (↓ better)",
    "metric.accuracy": "Prediction accuracy (↑ better)",
    "metric.sdv": "SDV score",
    "metric.validity": "Data validity",
    "metric.method": "Generation method",
    "metric.overall": "Overall quality score",
    "metric.overall.about": "How is this scored? → QualityEvaluator",

    "plots.tab.sdv": "Distributions",
    "plots.tab.corr": "Correlations",
    "plots.explore": "Explore column",
    "plots.select.placeholder": "— select column —",

    "status.uploading": "Uploading file...",
    "status.uploaded": "Dataset uploaded",
    "status.kaggle.missing": "Enter a Kaggle URL",
    "status.kaggle.loading": "Downloading from Kaggle (may take a while)...",
    "status.upload.error": "Upload failed",
    "status.kaggle.error": "Kaggle error",
    "status.gen.start": "Starting generation...",
    "status.gen.fail": "Could not start",
    "error.unknown": "Unknown error",
    "error.pandas":
      "Table processing error (pandas): column length mismatch during imputation.",

    "about.title": "About platform",
    "about.platform.title": "Platform",
    "about.platform.lead":
      'A web service for tabular data generation from an input dataset. Key feature: the platform automatically selects the most suitable generation method based on input dataset characteristics. Built on top of the <a href="https://github.com/MaratElagin/DataSynthesis131/tree/main/DataSynthesis131" target="_blank" rel="noopener">DataSynthesis131</a> library. Final qualification project: <a href="https://kai.ru/structure/general/institutes/institute-of-technical-cybernetics-and-informatics/" target="_blank" rel="noopener">institute-of-technical-cybernetics-and-informatics (ITCII, KAI)</a>, <a href="https://kpfu.ru/itis" target="_blank" rel="noopener">ITIS (KFU)</a>.',
    "about.platform.body2":
      "The platform follows an end-to-end workflow: upload source data, run structural analysis, launch synthesis with automatic or manual model selection, evaluate quality, and export final CSV.",
    "about.platform.caption": "Platform high-level architecture",
    "about.arch.alt": "Platform architecture diagram",
    "about.platform.flow.alt": "Main platform workflow",
    "about.platform.flow.caption": "Main workflow of the library and platform",
    "about.synth.title": "Synthesizer — how we choose the most suitable method",
    "about.synth.body":
      "Synthesizer analyzes class balance, feature types, dataset size, and speed constraints, then selects one method: Gaussian Copula, CTGAN, Copula GAN, or TVAE.",
    "about.synth.body2":
      "You can override the selected method manually and tune neural models with epochs to balance generation speed and sample quality.",
    "about.synth.alg.alt": "Generation method selection algorithm",
    "about.synth.alg.caption": "Automatic generation method selection algorithm",
    "about.methods.title": "Generation models",
    "about.methods.body":
      "Below is a short description of each generation model used in the platform.",
    "about.methods.body2":
      "Links point to the corresponding SDV synthesizer documentation.",
    "about.methods.gc":
      '<strong><a href="https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer" target="_blank" rel="noopener">Gaussian Copula</a></strong> — a fast statistical baseline, especially practical for mostly numerical tabular data.',
    "about.methods.ctgan":
      '<strong><a href="https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer" target="_blank" rel="noopener">CTGAN</a></strong> — neural model for richer feature dependencies and conditional distributions.',
    "about.methods.cgan":
      '<strong><a href="https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer" target="_blank" rel="noopener">Copula GAN</a></strong> — hybrid copula+GAN approach, often useful on smaller datasets.',
    "about.methods.tvae":
      '<strong><a href="https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer" target="_blank" rel="noopener">TVAE</a></strong> — variational autoencoder approach for mixed numerical/categorical tables.',
    "about.methods.auto":
      "<strong>Auto</strong> — library heuristic selects the method from dataset type, class balance, size, and speed constraints.",
    "about.methods.map.alt": "Library components map",
    "about.methods.map.caption": "Component and generation-mode mapping",
    "about.qe.title": "QualityEvaluator — how we evaluate generated data quality",
    "about.qe.body":
      "QualityEvaluator compares real and synthetic data using fidelity metrics: propensity score, log-cluster, and prediction accuracy.",
    "about.qe.body2":
      "Evaluation is built around fidelity metrics and supporting reports to estimate how closely synthetic data follows the source dataset.",
    "about.qe.metrics.lead": "Core metrics used in the platform:",
    "about.qe.metric.prop":
      '<strong>Propensity score (pMSE)</strong> — estimates how easily real and synthetic records can be separated; lower is better <a href="https://www.mdpi.com/2227-7390/11/15/3278" target="_blank" rel="noopener">(source)</a>.',
    "about.qe.metric.log":
      '<strong>Log-cluster metric</strong> — measures real/synthetic separability in clustering space <a href="https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-020-00977-1" target="_blank" rel="noopener">(source)</a>.',
    "about.qe.metric.pred":
      "<strong>Prediction accuracy</strong> — downstream model quality when trained on synthetic and evaluated on real target labels.",
    "about.qe.metric.sdv":
      '<strong>SDMetrics / Data validity / SDV score</strong> — additional statistical consistency and validity checks <a href="https://docs.sdv.dev/sdmetrics" target="_blank" rel="noopener">(docs)</a>.',
    "about.qe.dist.alt": "Real vs synthetic distribution match",
    "about.qe.dist.caption": "Example of real/synthetic distribution matching",
    "about.qe.table.alt": "TableEvaluator report snapshot",
    "about.qe.table.caption": "TableEvaluator report snapshot",
    "about.results.title": "Benchmark results",
    "about.results.body":
      "The benchmark compares models across multiple dataset families: numerical / categorical / mixed, as well as different class-balance profiles.",
    "about.results.body2":
      "This helps estimate not only average quality, but also method stability across realistic usage scenarios.",
    "about.results.chart.alt": "Model comparison chart",
    "about.results.chart.caption": "Example model comparison on weakly balanced numerical data",
    "about.results.link": "Benchmark table (Google Sheets)",
    "about.refs.title": "Research and references",
    "about.refs.readme": "Library README",
    "about.refs.colab": "Google Colab",
    "about.refs.video": "Video demo",
    "about.refs.notion": "Documentation (Notion)",

    "footer.api": "REST API",
    "footer.issues": "Issues",
    "footer.telegram": "Telegram",
  },
};

function getLang() {
  const stored = localStorage.getItem(I18N_STORAGE_KEY);
  if (stored === "ru" || stored === "en") return stored;
  return (navigator.language || "").toLowerCase().startsWith("en") ? "en" : "ru";
}

function t(key, vars = {}) {
  const lang = getLang();
  let value = STRINGS[lang][key] ?? STRINGS.ru[key] ?? key;
  Object.entries(vars).forEach(([k, v]) => {
    value = value.replaceAll(`{${k}}`, String(v));
  });
  return value;
}

function applyI18n(root = document) {
  document.documentElement.lang = getLang();
  root.querySelectorAll("[data-i18n]").forEach((el) => (el.textContent = t(el.dataset.i18n)));
  root.querySelectorAll("[data-i18n-html]").forEach(
    (el) => (el.innerHTML = t(el.dataset.i18nHtml))
  );
  root.querySelectorAll("[data-i18n-placeholder]").forEach(
    (el) => (el.placeholder = t(el.dataset.i18nPlaceholder))
  );
  root.querySelectorAll("[data-i18n-aria]").forEach((el) =>
    el.setAttribute("aria-label", t(el.dataset.i18nAria))
  );
  const label = document.getElementById("lang-label");
  if (label) label.textContent = getLang().toUpperCase();
  document.querySelectorAll("#lang-menu [data-lang]").forEach((el) => {
    el.classList.toggle("active", el.dataset.lang === getLang());
  });
}

function setLang(lang) {
  if (!["ru", "en"].includes(lang)) return;
  localStorage.setItem(I18N_STORAGE_KEY, lang);
  applyI18n();
  document.dispatchEvent(new CustomEvent("ds131:langchange"));
}

function initLangSwitcher() {
  const btn = document.getElementById("lang-btn");
  const menu = document.getElementById("lang-menu");
  if (!btn || !menu) return;

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    menu.classList.toggle("hidden");
    btn.setAttribute("aria-expanded", String(!menu.classList.contains("hidden")));
  });
  menu.querySelectorAll("[data-lang]").forEach((item) => {
    item.addEventListener("click", () => {
      setLang(item.dataset.lang);
      menu.classList.add("hidden");
      btn.setAttribute("aria-expanded", "false");
    });
  });
  document.addEventListener("click", () => {
    menu.classList.add("hidden");
    btn.setAttribute("aria-expanded", "false");
  });
}

window.I18n = { t, getLang, setLang, applyI18n };

function bootI18n() {
  applyI18n();
  initLangSwitcher();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootI18n);
} else {
  bootI18n();
}
