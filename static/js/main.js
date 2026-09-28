/* ============================================================
   ஊர் உழவன் - Landing page scripts (no animations)
   ============================================================ */
(function () {
    'use strict';

    const header = document.getElementById('siteHeader');

    /* ---------- Header height -> CSS var (for section scroll offset) ---------- */
    function setHeaderHeight() {
        if (!header) return;
        document.documentElement.style.setProperty('--header-h', header.offsetHeight + 'px');
    }
    setHeaderHeight();
    window.addEventListener('resize', setHeaderHeight);

    /* ---------- Mobile menu ---------- */
    const toggle = document.getElementById('navToggle');
    const menu = document.getElementById('mobileMenu');

    function setMenu(open) {
        if (!toggle || !menu) return;
        menu.hidden = !open;
        toggle.setAttribute('aria-expanded', String(open));
        toggle.innerHTML = open
            ? '<i class="fa-solid fa-xmark" aria-hidden="true"></i>'
            : '<i class="fa-solid fa-bars" aria-hidden="true"></i>';
    }

    if (toggle && menu) {
        toggle.addEventListener('click', function () {
            setMenu(menu.hidden);
        });
        menu.addEventListener('click', function (event) {
            if (event.target.closest('a')) setMenu(false);
        });
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') setMenu(false);
        });
        window.addEventListener('resize', function () {
            if (window.innerWidth > 1300) setMenu(false);
        });
    }

    /* ---------- Active nav link for the section in view ---------- */
    const links = Array.from(document.querySelectorAll('[data-nav-link]'));
    const sections = Array.from(new Set(links.map(function (link) {
        return document.querySelector(link.getAttribute('href'));
    }))).filter(Boolean);

    function setActive(id) {
        links.forEach(function (link) {
            link.classList.toggle('is-active', link.getAttribute('href') === '#' + id);
        });
    }

    function updateActive() {
        if (!sections.length) return;
        const offset = (header ? header.offsetHeight : 0) + 40;
        let current = sections[0].id;
        sections.forEach(function (section) {
            if (section.getBoundingClientRect().top - offset <= 0) current = section.id;
        });
        // Bottom of page: highlight the last section
        if (window.innerHeight + window.scrollY >= document.body.scrollHeight - 2) {
            current = sections[sections.length - 1].id;
        }
        setActive(current);
    }

    window.addEventListener('scroll', updateActive, { passive: true });
    updateActive();

    /* ---------- Carousels (categories, featured products) ----------
       Moves one card per arrow click, no sliding animation.
       Dots = number of scroll positions (cards - visible cards + 1). */
    document.querySelectorAll('[data-carousel]').forEach(function (carousel) {
        const name = carousel.getAttribute('data-carousel');
        const track = carousel.querySelector('[data-carousel-track]');
        const dotsBox = carousel.querySelector('[data-carousel-dots]');
        const arrows = document.querySelector('[data-carousel-arrows="' + name + '"]');
        const prev = arrows && arrows.querySelector('[data-carousel-prev]');
        const next = arrows && arrows.querySelector('[data-carousel-next]');
        if (!track || !track.children.length) return;

        function step() {
            const card = track.children[0];
            const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
            return card.getBoundingClientRect().width + gap;
        }

        function maxIndex() {
            const maxScroll = track.scrollWidth - track.clientWidth;
            return maxScroll <= 1 ? 0 : Math.ceil(maxScroll / step() - 0.05);
        }

        function maxScroll() {
            return track.scrollWidth - track.clientWidth;
        }

        function currentIndex() {
            if (track.scrollLeft >= maxScroll() - 2) return maxIndex();
            return Math.min(maxIndex(), Math.round(track.scrollLeft / step()));
        }

        function goTo(index) {
            index = Math.max(0, Math.min(maxIndex(), index));
            // Last position: scroll fully to the end so the last card is never cut off
            const left = index === maxIndex() ? maxScroll() : index * step();
            track.scrollTo({ left: left, behavior: 'instant' });
            update();
        }

        function buildDots() {
            if (!dotsBox) return;
            const count = maxIndex() + 1;
            dotsBox.innerHTML = '';
            if (count < 2) return;
            for (let i = 0; i < count; i++) {
                const dot = document.createElement('button');
                dot.type = 'button';
                dot.className = 'carousel__dot';
                dot.setAttribute('aria-label', 'Slide ' + (i + 1));
                dot.addEventListener('click', function () { goTo(i); });
                dotsBox.appendChild(dot);
            }
        }

        function update() {
            const index = currentIndex();
            const last = maxIndex();
            if (dotsBox) {
                Array.from(dotsBox.children).forEach(function (dot, i) {
                    dot.classList.toggle('is-active', i === index);
                    dot.setAttribute('aria-current', i === index ? 'true' : 'false');
                });
            }
            if (prev) prev.disabled = index <= 0;
            if (next) next.disabled = index >= last;
            if (arrows) arrows.hidden = last === 0;
        }

        if (prev) prev.addEventListener('click', function () { goTo(currentIndex() - 1); });
        if (next) next.addEventListener('click', function () { goTo(currentIndex() + 1); });
        track.addEventListener('scroll', update, { passive: true });

        // Rebuild dots whenever the carousel width changes (resize, rotate, fonts loaded)
        let lastWidth = 0;
        const refresh = function () {
            if (track.clientWidth === lastWidth) return;
            lastWidth = track.clientWidth;
            buildDots();
            update();
        };
        if ('ResizeObserver' in window) {
            new ResizeObserver(refresh).observe(track);
        } else {
            window.addEventListener('resize', refresh);
        }

        buildDots();
        update();
    });

    /* ---------- Wholesale enquiry form ----------
       Same rules as the server (landing/forms.py); the server checks again. */
    const form = document.getElementById('enquiryForm');
    if (form) initEnquiryForm(form);

    function initEnquiryForm(form) {
        const fileInput = document.getElementById('enquiryFiles');
        const uploadBox = document.getElementById('uploadBox');
        const uploadList = document.getElementById('uploadList');
        const formError = document.getElementById('formError');
        const submitBtn = document.getElementById('enquirySubmit');
        const submitText = submitBtn.querySelector('.enquiry-submit__text');
        const success = document.getElementById('formSuccess');
        const successText = document.getElementById('formSuccessText');
        const successWa = document.getElementById('formSuccessWa');
        const againBtn = document.getElementById('formAgain');

        const maxFiles = parseInt(form.dataset.maxFiles, 10) || 5;
        const maxBytes = (parseInt(form.dataset.maxMb, 10) || 10) * 1024 * 1024;
        const extensions = (form.dataset.extensions || '').split(',');
        const openWhatsapp = form.dataset.openWhatsapp === '1';
        const originalSubmitText = submitText.textContent;
        let files = [];

        const URL_PATTERN = /(https?:\/\/|www\.|\.com\b|\.in\b|\.net\b|<[^>]+>)/i;
        const LENGTHS = {
            business_name: [2, 150], contact_person: [2, 100], delivery_location: [5, 300],
            required_products: [2, 2000], quantity: [1, 200], message: [0, 2000]
        };

        const clean = function (v) { return (v || '').replace(/[ \t]+/g, ' ').trim(); };
        const hasLetter = function (v) { return /\p{L}/u.test(v); };

        function fieldBox(name) { return form.querySelector('[data-field="' + name + '"]'); }

        function shortLabel(name) {
            const box = fieldBox(name);
            const label = box ? box.querySelector('.field__label').textContent : name;
            return label.replace('*', '').split(' (')[0].trim();
        }

        function setError(name, message) {
            const el = document.getElementById('err-' + name);
            if (el) el.textContent = message || '';
            const box = name === 'files' ? uploadBox : fieldBox(name);
            if (box) box.classList.toggle('has-error', !!message);
        }

        function clearErrors() {
            form.querySelectorAll('.field__error').forEach(function (el) { el.textContent = ''; });
            form.querySelectorAll('.has-error').forEach(function (el) { el.classList.remove('has-error'); });
            uploadBox.classList.remove('has-error');
            formError.hidden = true;
            formError.textContent = '';
        }

        /* --- files --- */
        function formatSize(bytes) {
            return bytes >= 1048576 ? (bytes / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(bytes / 1024)) + ' KB';
        }

        function fileIcon(ext) {
            if (ext === 'pdf') return 'fa-file-pdf';
            if (['xls', 'xlsx', 'csv'].indexOf(ext) !== -1) return 'fa-file-excel';
            if (['doc', 'docx', 'txt'].indexOf(ext) !== -1) return 'fa-file-word';
            return 'fa-file-image';
        }

        function extOf(name) { return (name.split('.').pop() || '').toLowerCase(); }

        function renderFiles() {
            uploadList.innerHTML = '';
            files.forEach(function (file, index) {
                const li = document.createElement('li');
                li.className = 'upload-file';
                li.innerHTML = '<i class="fa-regular ' + fileIcon(extOf(file.name)) + ' upload-file__icon" aria-hidden="true"></i>' +
                    '<span class="upload-file__name"></span><span class="upload-file__size"></span>' +
                    '<button type="button" class="upload-file__remove" aria-label="Remove"><i class="fa-solid fa-xmark" aria-hidden="true"></i></button>';
                li.querySelector('.upload-file__name').textContent = file.name;
                li.querySelector('.upload-file__size').textContent = formatSize(file.size);
                li.querySelector('button').addEventListener('click', function () {
                    files.splice(index, 1);
                    renderFiles();
                    setError('files', '');
                });
                uploadList.appendChild(li);
            });
        }

        function addFiles(list) {
            const problems = [];
            Array.from(list).forEach(function (file) {
                const ext = extOf(file.name);
                if (extensions.indexOf(ext) === -1) {
                    problems.push('"' + file.name + '" - இந்த வகை கோப்பு அனுமதிக்கப்படாது (PDF, படம், Excel, Word மட்டும்).');
                } else if (file.size === 0) {
                    problems.push('"' + file.name + '" - கோப்பு காலியாக உள்ளது.');
                } else if (file.size > maxBytes) {
                    problems.push('"' + file.name + '" - கோப்பின் அளவு ' + (maxBytes / 1048576) + ' MB-க்கு மேல் இருக்கக்கூடாது.');
                } else if (files.length >= maxFiles) {
                    problems.push('அதிகபட்சம் ' + maxFiles + ' கோப்புகள் மட்டுமே பதிவேற்றலாம்.');
                } else if (!files.some(function (f) { return f.name === file.name && f.size === file.size; })) {
                    files.push(file);
                }
            });
            renderFiles();
            setError('files', Array.from(new Set(problems)).join(' '));
            fileInput.value = '';
        }

        fileInput.addEventListener('change', function () { addFiles(fileInput.files); });

        ['dragenter', 'dragover'].forEach(function (type) {
            uploadBox.addEventListener(type, function (event) {
                event.preventDefault();
                uploadBox.classList.add('is-dragover');
            });
        });
        ['dragleave', 'drop'].forEach(function (type) {
            uploadBox.addEventListener(type, function (event) {
                event.preventDefault();
                uploadBox.classList.remove('is-dragover');
            });
        });
        uploadBox.addEventListener('drop', function (event) {
            if (event.dataTransfer && event.dataTransfer.files.length) addFiles(event.dataTransfer.files);
        });

        /* --- field rules --- */
        function validateField(el) {
            const name = el.name;
            const value = el.tagName === 'TEXTAREA' ? (el.value || '').trim() : clean(el.value);
            const label = shortLabel(name);
            const required = el.required || (name === 'required_products' && el.dataset.requiredWhenNoFile === '1');

            if (!value) {
                if (name === 'required_products' && el.dataset.requiredWhenNoFile === '1' && files.length) return '';
                if (required) {
                    return name === 'required_products'
                        ? 'தேவையான பொருட்களை உள்ளிடவும் அல்லது பட்டியல் கோப்பை பதிவேற்றவும்.'
                        : label + ' கட்டாயம் நிரப்ப வேண்டும்.';
                }
                return '';
            }

            if (LENGTHS[name]) {
                if (value.length < LENGTHS[name][0]) return label + ' குறைந்தது ' + LENGTHS[name][0] + ' எழுத்துகள் இருக்க வேண்டும்.';
                if (value.length > LENGTHS[name][1]) return label + ' அதிகபட்சம் ' + LENGTHS[name][1] + ' எழுத்துகள் மட்டுமே.';
                if (URL_PATTERN.test(value)) return label + ' பகுதியில் இணைய முகவரி (link) அனுமதிக்கப்படாது.';
            }

            switch (name) {
                case 'business_name':
                    if (!hasLetter(value)) return 'வணிகப் பெயரில் எழுத்துகள் இருக்க வேண்டும்.';
                    break;
                case 'contact_person':
                    if (!hasLetter(value) || !/^[\p{L}\p{M} .'-]+$/u.test(value)) {
                        return 'பெயரில் எழுத்துகள் மட்டுமே இருக்க வேண்டும் (எண்கள் / குறியீடுகள் வேண்டாம்).';
                    }
                    break;
                case 'mobile': {
                    let digits = value.replace(/\D/g, '');
                    if (digits.length === 12 && digits.indexOf('91') === 0) digits = digits.slice(2);
                    else if (digits.length === 11 && digits[0] === '0') digits = digits.slice(1);
                    if (!/^[6-9]\d{9}$/.test(digits)) return 'சரியான 10 இலக்க மொபைல் எண்ணை உள்ளிடவும் (6, 7, 8 அல்லது 9-ல் தொடங்க வேண்டும்).';
                    if (/^(\d)\1{9}$/.test(digits)) return 'சரியான மொபைல் எண்ணை உள்ளிடவும்.';
                    break;
                }
                case 'delivery_location':
                    if (!hasLetter(value)) return 'சரியான விநியோக முகவரியை உள்ளிடவும்.';
                    break;
                case 'delivery_date':
                    if (el.min && value < el.min) return 'விநியோக தேதி இன்று அல்லது அதற்குப் பிறகு இருக்க வேண்டும்.';
                    if (el.max && value > el.max) return 'விநியோக தேதி ஒரு வருடத்திற்குள் இருக்க வேண்டும்.';
                    break;
                case 'required_products':
                    if (!hasLetter(value)) return 'தேவையான பொருட்களின் பெயர்களை உள்ளிடவும்.';
                    break;
                case 'quantity':
                    if (!/\d/.test(value)) return 'அளவை எண்ணுடன் குறிப்பிடவும் (எ.கா. 50 kg, 10 மூட்டை).';
                    break;
            }
            return '';
        }

        // Products are optional when a list file is uploaded
        const productsInput = form.querySelector('[name="required_products"]');
        if (productsInput && productsInput.required) {
            productsInput.required = false;
            productsInput.dataset.requiredWhenNoFile = '1';
        }

        const inputs = Array.from(form.querySelectorAll('.field input, .field select, .field textarea'));
        inputs.forEach(function (el) {
            el.addEventListener('blur', function () {
                if (el.value) setError(el.name, validateField(el));
            });
            el.addEventListener('input', function () {
                const box = fieldBox(el.name);
                if (box && box.classList.contains('has-error')) setError(el.name, validateField(el));
            });
        });

        /* --- submit --- */
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            clearErrors();

            let firstInvalid = null;
            inputs.forEach(function (el) {
                const message = validateField(el);
                if (message) {
                    setError(el.name, message);
                    if (!firstInvalid) firstInvalid = el;
                }
            });
            if (firstInvalid) {
                firstInvalid.focus();
                return;
            }

            const data = new FormData();
            data.append('csrfmiddlewaretoken', form.querySelector('[name="csrfmiddlewaretoken"]').value);
            data.append('website', form.querySelector('[name="website"]').value);
            inputs.forEach(function (el) { data.append(el.name, el.value.trim()); });
            files.forEach(function (file) { data.append('files', file, file.name); });

            submitBtn.disabled = true;
            submitText.textContent = 'அனுப்புகிறது…';

            fetch(form.action, {
                method: 'POST',
                body: data,
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin'
            })
                .then(function (response) {
                    return response.json().catch(function () { return { ok: false }; });
                })
                .then(function (result) {
                    if (result.ok) {
                        showSuccess(result);
                        return;
                    }
                    const errors = result.errors || {};
                    let focused = false;
                    Object.keys(errors).forEach(function (name) {
                        const message = errors[name].map(function (e) { return e.message || e; }).join(' ');
                        if (name === '__all__' || !fieldBox(name)) {
                            formError.textContent = (formError.textContent + ' ' + message).trim();
                            formError.hidden = false;
                        } else {
                            setError(name, message);
                            if (!focused) {
                                const el = form.querySelector('[name="' + name + '"]');
                                if (el) el.focus();
                                focused = true;
                            }
                        }
                    });
                    if (!Object.keys(errors).length) {
                        formError.textContent = 'ஏதோ பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்.';
                        formError.hidden = false;
                    }
                })
                .catch(function () {
                    formError.textContent = 'இணைய இணைப்பில் பிழை. மீண்டும் முயற்சிக்கவும்.';
                    formError.hidden = false;
                })
                .finally(function () {
                    submitBtn.disabled = false;
                    submitText.textContent = originalSubmitText;
                });
        });

        function showSuccess(result) {
            form.hidden = true;
            success.hidden = false;
            if (result.message) successText.textContent = result.message;
            if (result.whatsapp_url) {
                successWa.href = result.whatsapp_url;
                successWa.hidden = false;
                if (openWhatsapp) window.open(result.whatsapp_url, '_blank', 'noopener');
            }
            success.scrollIntoView({ block: 'center' });
        }

        againBtn.addEventListener('click', function () {
            form.reset();
            files = [];
            renderFiles();
            clearErrors();
            success.hidden = true;
            successWa.hidden = true;
            form.hidden = false;
        });
    }
})();
