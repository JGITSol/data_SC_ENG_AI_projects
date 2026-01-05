document.addEventListener('DOMContentLoaded', () => {
    const LANG_KEY = 'lang';
    const THEME_KEY = 'theme';

    const uiTranslations = {
        en: {
            skip: 'Skip to main content',
            navAria: 'Site navigation',
            home: 'Home',
            back: 'Back',
            backAria: 'Go back',
            docs: 'Docs',
            docsAria: 'Open documentation',
            themeAria: 'Toggle theme',
            langAria: 'Language',
            light: 'Light',
            dark: 'Dark'
        },
        pl: {
            skip: 'Przejdź do treści',
            navAria: 'Nawigacja',
            home: 'Strona główna',
            back: 'Wstecz',
            backAria: 'Wróć',
            docs: 'Dokumentacja',
            docsAria: 'Otwórz dokumentację',
            themeAria: 'Przełącz motyw',
            langAria: 'Język',
            light: 'Jasny',
            dark: 'Ciemny'
        }
    };

    const normalizeLang = (raw) => {
        const l = (raw || '').toLowerCase();
        if (l === 'ua') return 'uk';
        return uiTranslations[l] ? l : 'en';
    };

    let lang = normalizeLang(localStorage.getItem(LANG_KEY));
    const storedThemeRaw = localStorage.getItem(THEME_KEY);
    let theme = (storedThemeRaw || '').toLowerCase();
    if (theme !== 'dark' && theme !== 'light') {
        theme = (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)
            ? 'dark'
            : 'light';
    }
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('lang', lang);

    const body = document.body;
    const pageName = body.dataset.pageName || document.title || 'Data Lab';
    const guide = body.dataset.guide;
    const home = body.dataset.home || './index.html';
    const labName = body.dataset.labName || 'Data Lab';
    const tags = (body.dataset.tags || '')
        .split(',')
        .map(t => t.trim())
        .filter(Boolean);

    const getT = () => uiTranslations[lang] || uiTranslations.en;

    const nameTranslations = {
        lab: {
            en: 'Data & AI Lab',
            pl: 'Laboratorium Danych i AI'
        },
        page: {
            'Data & AI Lab': {
                en: 'Data & AI Lab',
                pl: 'Laboratorium Danych i AI'
            },
            'Neural Network Visualizer': {
                en: 'Neural Network Visualizer',
                pl: 'Wizualizacja Sieci Neuronowej'
            },
            'Clustering Playground': {
                en: 'Clustering Playground',
                pl: 'Symulator Klastrowania'
            },
            'Genetic Algorithms & Evolution': {
                en: 'Genetic Algorithms & Evolution',
                pl: 'Algorytmy Genetyczne i Ewolucja'
            }
        }
    };

    const translateLabName = () => {
        if (labName !== 'Data Lab') return labName;
        return nameTranslations.lab[lang] || nameTranslations.lab.en || labName;
    };

    const translatePageName = () => {
        const dict = nameTranslations.page[pageName];
        const t = dict?.[lang] || dict?.en;
        return t || pageName;
    };

    const setTheme = (nextTheme) => {
        theme = nextTheme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(THEME_KEY, theme);

        const t = getT();
        document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
            btn.innerHTML = `<i data-lucide="${theme === 'dark' ? 'sun' : 'moon'}"></i>`;
            // Dynamic accessibility label
            btn.setAttribute('aria-label', t.themeAria);
        });
        if (window.lucide) window.lucide.createIcons();

        window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
    };

    const setLang = (nextLang) => {
        lang = normalizeLang(nextLang);
        localStorage.setItem(LANG_KEY, lang);
        document.documentElement.setAttribute('lang', lang);

        const t = getT();

        document.querySelectorAll('[data-lang-select]').forEach(select => {
            if (select.value !== lang) select.value = lang;
            select.setAttribute('aria-label', t.langAria);
        });

        document.querySelectorAll('[data-i18n-ui]').forEach(el => {
            const key = el.getAttribute('data-i18n-ui');
            if (!key) return;
            if (t[key]) el.textContent = t[key];
        });

        document.querySelectorAll('[data-i18n-name="lab"]').forEach(el => {
            el.textContent = translateLabName();
        });

        document.querySelectorAll('[data-i18n-name="page"]').forEach(el => {
            el.textContent = translatePageName();
        });

        // Add additional translation logic here...
        const pageTranslations = window.PAGE_TRANSLATIONS;
        const pageDict = (pageTranslations && (pageTranslations[lang] || pageTranslations.en)) || {};

        const setText = (el, value) => {
            if (value === undefined || value === null) return;
            el.textContent = String(value);
        };

        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (!key) return;
            setText(el, pageDict[key]);
        });

        const onChange = window.PAGE_I18N_ONCHANGE;
        if (typeof onChange === 'function') {
            try {
                onChange(lang, pageDict);
            } catch (e) { }
        }

        setTheme(theme);
        window.dispatchEvent(new CustomEvent('langchange', { detail: { lang } }));
    };

    const ensureMainTarget = () => {
        const existing = document.getElementById('main-content');
        if (existing) return existing;

        const candidate = document.querySelector('main')
            || document.querySelector('.lab-shell')
            || document.querySelector('.container')
            || document.querySelector('body > *');

        if (!candidate) return null;

        candidate.id = 'main-content';
        if (candidate.tagName.toLowerCase() !== 'main') {
            candidate.setAttribute('role', 'main');
        }
        if (!candidate.hasAttribute('tabindex')) {
            candidate.setAttribute('tabindex', '-1');
        }
        return candidate;
    };

    ensureMainTarget();

    const skip = document.createElement('a');
    skip.className = 'skip-link';
    skip.href = '#main-content';
    skip.setAttribute('data-i18n-ui', 'skip');
    skip.textContent = getT().skip;
    document.body.prepend(skip);

    const nav = document.createElement('nav');
    nav.className = 'lab-nav';
    nav.setAttribute('aria-label', getT().navAria);
    nav.innerHTML = `
        <div class="lab-brand">
            <span class="dot"></span>
            <a class="lab-brand-name" href="${home}" data-i18n-name="lab">${translateLabName()}</a>
            <span class="lab-divider">/</span>
            <span class="lab-current" data-i18n-name="page">${translatePageName()}</span>
        </div>
        <div class="lab-actions">
            <select class="pill ghost" data-lang-select aria-label="${getT().langAria}">
                <option value="en">EN</option>
                <option value="pl">PL</option>
            </select>
            <button class="pill ghost theme-toggle-btn" type="button" data-theme-toggle>
                <i data-lucide="${theme === 'dark' ? 'sun' : 'moon'}"></i>
            </button>
        </div>
    `;


    nav.querySelectorAll('[data-theme-toggle]').forEach(btn => {
        btn.addEventListener('click', () => {
            setTheme(theme === 'dark' ? 'light' : 'dark');
        });
    });

    nav.querySelectorAll('[data-lang-select]').forEach(select => {
        select.value = lang;
        select.addEventListener('change', (e) => {
            setLang(e.target.value);
        });
    });

    document.body.prepend(nav);

    if (tags.length) {
        const tagBar = document.createElement('div');
        tagBar.className = 'lab-tagbar';
        tagBar.innerHTML = tags.map(tag => `<span class="tag">${tag}</span>`).join('');
        nav.after(tagBar);
    }

    setTheme(theme);
    setLang(lang);
});
