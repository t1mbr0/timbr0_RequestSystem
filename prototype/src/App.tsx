import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import {
  ArrowLeft, ArrowRight, BellRing, Check, CheckCircle2, ChevronDown, CircleHelp,
  ClipboardList, Clock3, Eye, EyeOff, FilePlus2, FilterX, Inbox, LoaderCircle,
  LogOut, Menu, Pencil, Search, ShieldCheck, Trash2, UserRound,
  UsersRound, X, AlertTriangle, Building2, CalendarDays, Send, Paperclip,
} from 'lucide-react'
import './App.css'

type Status = 'Новая' | 'В работе' | 'Ожидает' | 'Закрыта'
type Priority = 'Низкий' | 'Средний' | 'Высокий'
type View = 'login' | 'list' | 'create' | 'details' | 'edit'
type Comment = { author: string; text: string; time: string }
type RequestItem = {
  id: number; title: string; category: string; status: Status; priority: Priority
  applicant: string; assignee: string; created: string; deadline: string
  description: string; comments: Comment[]; history: string[]
}
type RequestDraft = {
  title: string; category: string; applicant: string; priority: Priority
  assignee: string; description: string; status: Status; deadline: string
}

const initialRequests: RequestItem[] = [
  {
    id: 1042, title: 'Не работает проектор в аудитории 214', category: 'Оборудование', status: 'Новая', priority: 'Высокий',
    applicant: 'Ирина Соколова', assignee: 'Не назначен', created: '03.11.2026, 09:14', deadline: '04.11.2026',
    description: 'Проектор не включается, индикатор питания не горит. В 11:30 в аудитории запланирована лекция, нужна помощь специалиста.',
    comments: [], history: ['03.11.2026, 09:14 — заявка зарегистрирована'],
  },
  {
    id: 1041, title: 'Восстановить доступ к учебному порталу', category: 'Доступ', status: 'В работе', priority: 'Средний',
    applicant: 'Алексей Морозов', assignee: 'Мария Волкова', created: '02.11.2026, 16:42', deadline: '04.11.2026',
    description: 'После смены пароля не удаётся войти в личный кабинет. Ошибка появляется и в браузере, и в мобильном приложении.',
    comments: [{ author: 'Мария Волкова', text: 'Проверяю состояние учётной записи в каталоге.', time: '03.11.2026, 08:55' }],
    history: ['02.11.2026, 16:42 — заявка зарегистрирована', '03.11.2026, 08:50 — назначен исполнитель Мария Волкова'],
  },
  {
    id: 1039, title: 'Медленно работает Wi-Fi в библиотеке', category: 'Сеть', status: 'Ожидает', priority: 'Средний',
    applicant: 'Олег Никитин', assignee: 'Денис Орлов', created: '01.11.2026, 12:20', deadline: '05.11.2026',
    description: 'Скорость соединения резко падает во второй половине дня. Проблема повторяется на нескольких устройствах.',
    comments: [{ author: 'Денис Орлов', text: 'Нужны замеры скорости после 15:00 для диагностики.', time: '02.11.2026, 10:12' }],
    history: ['01.11.2026, 12:20 — заявка зарегистрирована', '02.11.2026, 10:12 — ожидаются сведения от заявителя'],
  },
  {
    id: 1036, title: 'Установить офисный пакет на рабочее место', category: 'Программы', status: 'Закрыта', priority: 'Низкий',
    applicant: 'Елена Белова', assignee: 'Мария Волкова', created: '29.10.2026, 10:05', deadline: '31.10.2026',
    description: 'На новый компьютер методиста необходимо установить лицензионный офисный пакет и настроить печать документов.',
    comments: [{ author: 'Мария Волкова', text: 'Программы установлены, печать проверена.', time: '30.10.2026, 14:32' }],
    history: ['29.10.2026, 10:05 — заявка зарегистрирована', '30.10.2026, 14:32 — работа завершена', '30.10.2026, 15:10 — закрытие подтверждено'],
  },
  {
    id: 1034, title: 'Заменить клавиатуру в компьютерном классе', category: 'Оборудование', status: 'В работе', priority: 'Низкий',
    applicant: 'Павел Егоров', assignee: 'Денис Орлов', created: '28.10.2026, 13:37', deadline: '06.11.2026',
    description: 'На рабочем месте 12 не работают несколько клавиш. Требуется диагностика и замена клавиатуры.',
    comments: [], history: ['28.10.2026, 13:37 — заявка зарегистрирована', '29.10.2026, 09:05 — назначен исполнитель Денис Орлов'],
  },
]

const emptyDraft: RequestDraft = {
  title: '', category: '', applicant: '', priority: 'Средний', assignee: 'Не назначен',
  description: '', status: 'Новая', deadline: '2026-11-10',
}
const categories = ['Оборудование', 'Доступ', 'Сеть', 'Программы', 'Другое']
const assignees = ['Не назначен', 'Мария Волкова', 'Денис Орлов']
const statuses: Status[] = ['Новая', 'В работе', 'Ожидает', 'Закрыта']

function loadRequests() {
  try {
    const saved = localStorage.getItem('request-system-prototype')
    return saved ? JSON.parse(saved) as RequestItem[] : initialRequests
  } catch { return initialRequests }
}
function number(id: number) { return `ЗАЯВКА #${id}` }
function nowLabel() { return new Date().toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) }

export default function App() {
  const [requests, setRequests] = useState<RequestItem[]>(loadRequests)
  const [view, setView] = useState<View>('login')
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('Все статусы')
  const [categoryFilter, setCategoryFilter] = useState('Все категории')
  const [draft, setDraft] = useState<RequestDraft>(emptyDraft)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [login, setLogin] = useState('operator')
  const [password, setPassword] = useState('12345')
  const [showPassword, setShowPassword] = useState(false)
  const [loginError, setLoginError] = useState('')
  const [loginLoading, setLoginLoading] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [helpOpen, setHelpOpen] = useState(false)
  const [mobileMenu, setMobileMenu] = useState(false)
  const [comment, setComment] = useState('')
  const [commentError, setCommentError] = useState('')
  const [toast, setToast] = useState('')

  const selected = requests.find(item => item.id === selectedId) ?? null
  const filtered = useMemo(() => requests.filter(item => {
    const query = search.trim().toLowerCase()
    return (!query || item.title.toLowerCase().includes(query) || String(item.id).includes(query))
      && (statusFilter === 'Все статусы' || item.status === statusFilter)
      && (categoryFilter === 'Все категории' || item.category === categoryFilter)
  }), [requests, search, statusFilter, categoryFilter])

  useEffect(() => { localStorage.setItem('request-system-prototype', JSON.stringify(requests)) }, [requests])
  useEffect(() => {
    if (!toast) return
    const timer = window.setTimeout(() => setToast(''), 3500)
    return () => window.clearTimeout(timer)
  }, [toast])
  useEffect(() => {
    const close = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { setDeleteOpen(false); setHelpOpen(false); setMobileMenu(false) }
    }
    window.addEventListener('keydown', close)
    return () => window.removeEventListener('keydown', close)
  }, [])

  function openRequest(id: number) { setSelectedId(id); setView('details'); setComment(''); setCommentError(''); window.scrollTo(0, 0) }
  function goCreate() { setDraft(emptyDraft); setErrors({}); setView('create'); setMobileMenu(false); window.scrollTo(0, 0) }
  function goList() { setView('list'); setSelectedId(null); setMobileMenu(false); window.scrollTo(0, 0) }
  function goEdit() {
    if (!selected) return
    setDraft({ title: selected.title, category: selected.category, applicant: selected.applicant, priority: selected.priority,
      assignee: selected.assignee, description: selected.description, status: selected.status, deadline: selected.deadline.split('.').reverse().join('-') })
    setErrors({}); setView('edit'); window.scrollTo(0, 0)
  }
  function validateDraft() {
    const next: Record<string, string> = {}
    if (draft.title.trim().length < 5) next.title = 'Укажите тему — не менее 5 символов'
    if (!draft.category) next.category = 'Выберите категорию обращения'
    if (draft.applicant.trim().length < 3) next.applicant = 'Укажите фамилию и имя заявителя'
    if (draft.description.trim().length < 20) next.description = 'Опишите проблему подробнее — не менее 20 символов'
    if (!draft.deadline) next.deadline = 'Укажите желаемый срок'
    setErrors(next)
    return Object.keys(next).length === 0
  }
  function submitDraft(event: FormEvent) {
    event.preventDefault()
    if (!validateDraft()) return
    if (view === 'create') {
      const id = Math.max(...requests.map(item => item.id), 1042) + 1
      const created = nowLabel()
      const item: RequestItem = { id, ...draft, title: draft.title.trim(), applicant: draft.applicant.trim(),
        description: draft.description.trim(), created, deadline: draft.deadline.split('-').reverse().join('.'), comments: [],
        history: [`${created} — заявка зарегистрирована`] }
      setRequests(current => [item, ...current]); setSelectedId(id); setView('details'); setToast(`Заявка #${id} успешно создана`)
    } else if (selected) {
      setRequests(current => current.map(item => item.id === selected.id ? { ...item, ...draft,
        title: draft.title.trim(), applicant: draft.applicant.trim(), description: draft.description.trim(),
        deadline: draft.deadline.split('-').reverse().join('.'), history: [...item.history, `${nowLabel()} — сведения заявки обновлены`] } : item))
      setView('details'); setToast('Изменения сохранены')
    }
    window.scrollTo(0, 0)
  }
  function takeInWork() {
    if (!selected) return
    setRequests(current => current.map(item => item.id === selected.id ? { ...item, status: 'В работе', assignee: 'Мария Волкова',
      history: [...item.history, `${nowLabel()} — заявка принята в работу`] } : item))
    setToast('Заявка принята в работу')
  }
  function addComment(event: FormEvent) {
    event.preventDefault()
    if (comment.trim().length < 3) { setCommentError('Введите комментарий — не менее 3 символов'); return }
    if (!selected) return
    setRequests(current => current.map(item => item.id === selected.id ? { ...item,
      comments: [...item.comments, { author: 'Тимофей Гатин', text: comment.trim(), time: nowLabel() }],
      history: [...item.history, `${nowLabel()} — добавлен комментарий`] } : item))
    setComment(''); setCommentError(''); setToast('Комментарий добавлен')
  }
  function deleteRequest() {
    if (!selected) return
    const id = selected.id
    setRequests(current => current.filter(item => item.id !== id)); setDeleteOpen(false); goList(); setToast(`Заявка #${id} удалена`)
  }
  function resetFilters() { setSearch(''); setStatusFilter('Все статусы'); setCategoryFilter('Все категории') }
  function signIn(event: FormEvent) {
    event.preventDefault(); setLoginError('')
    if (login.trim() !== 'operator' || password !== '12345') { setLoginError('Неверный логин или пароль. Проверьте данные и повторите попытку.'); return }
    setLoginLoading(true)
    window.setTimeout(() => { setLoginLoading(false); setView('list') }, 450)
  }

  if (view === 'login') return <LoginScreen login={login} password={password} showPassword={showPassword} error={loginError}
    loading={loginLoading} setLogin={setLogin} setPassword={setPassword} setShowPassword={setShowPassword} onSubmit={signIn} />

  return <div className="app-shell">
    <aside className={`sidebar ${mobileMenu ? 'sidebar-open' : ''}`}>
      <div className="brand"><div className="brand-mark"><ClipboardList size={22} /></div><div><strong>Заявки</strong><span>RequestSystem</span></div></div>
      <button className="sidebar-close icon-button" onClick={() => setMobileMenu(false)} aria-label="Закрыть меню"><X size={20} /></button>
      <nav className="main-nav" aria-label="Основная навигация">
        <span className="nav-caption">Рабочее пространство</span>
        <button className={view === 'list' || view === 'details' || view === 'edit' ? 'nav-item active' : 'nav-item'} onClick={goList}><Inbox size={19} />Все заявки<span className="nav-count">{requests.length}</span></button>
        <button className={view === 'create' ? 'nav-item active' : 'nav-item'} onClick={goCreate}><FilePlus2 size={19} />Новая заявка</button>
        <button className="nav-item" onClick={() => { setHelpOpen(true); setMobileMenu(false) }}><CircleHelp size={19} />Справка</button>
      </nav>
      <div className="sidebar-note"><ShieldCheck size={19} /><div><strong>Учебный прототип</strong><span>Данные хранятся только в этом браузере</span></div></div>
      <div className="profile"><div className="avatar">ТГ</div><div><strong>Тимофей Гатин</strong><span>Оператор</span></div><button className="icon-button" onClick={() => setView('login')} aria-label="Выйти"><LogOut size={18} /></button></div>
    </aside>
    {mobileMenu && <button className="sidebar-backdrop" onClick={() => setMobileMenu(false)} aria-label="Закрыть меню" />}

    <main className="main-area">
      <header className="topbar">
        <button className="mobile-menu icon-button" onClick={() => setMobileMenu(true)} aria-label="Открыть меню"><Menu size={21} /></button>
        <div className="breadcrumbs"><span>RequestSystem</span><span>/</span><strong>{view === 'list' ? 'Все заявки' : view === 'create' ? 'Новая заявка' : view === 'edit' ? `Редактирование #${selectedId}` : `Заявка #${selectedId}`}</strong></div>
        <div className="topbar-status"><span className="online-dot" />Система работает</div>
      </header>

      <div className="content">
        {view === 'list' && <>
          <section className="page-heading"><div><h1>Заявки</h1><p>Контролируйте обращения и сроки их выполнения</p></div><button className="button primary" onClick={goCreate}><FilePlus2 size={18} />Создать заявку</button></section>
          <section className="stats-grid" aria-label="Статистика заявок">
            <button className="stat-card" onClick={resetFilters}><span className="stat-icon slate"><ClipboardList size={20} /></span><div><span>Всего заявок</span><strong>{requests.length}</strong></div><ArrowRight size={17} /></button>
            <button className="stat-card" onClick={() => setStatusFilter('Новая')}><span className="stat-icon blue"><BellRing size={20} /></span><div><span>Новые</span><strong>{requests.filter(item => item.status === 'Новая').length}</strong></div><ArrowRight size={17} /></button>
            <button className="stat-card" onClick={() => setStatusFilter('В работе')}><span className="stat-icon amber"><LoaderCircle size={20} /></span><div><span>В работе</span><strong>{requests.filter(item => item.status === 'В работе').length}</strong></div><ArrowRight size={17} /></button>
            <button className="stat-card" onClick={() => setStatusFilter('Закрыта')}><span className="stat-icon green"><CheckCircle2 size={20} /></span><div><span>Закрыты</span><strong>{requests.filter(item => item.status === 'Закрыта').length}</strong></div><ArrowRight size={17} /></button>
          </section>
          <section className="requests-panel">
            <div className="filters"><label className="search-field"><Search size={18} /><input value={search} onChange={event => setSearch(event.target.value)} placeholder="Номер или тема заявки" aria-label="Поиск заявок" />{search && <button onClick={() => setSearch('')} aria-label="Очистить поиск"><X size={16} /></button>}</label>
              <label className="select-wrap"><span className="sr-only">Фильтр по статусу</span><select value={statusFilter} onChange={event => setStatusFilter(event.target.value)}><option>Все статусы</option>{statuses.map(item => <option key={item}>{item}</option>)}</select><ChevronDown size={16} /></label>
              <label className="select-wrap"><span className="sr-only">Фильтр по категории</span><select value={categoryFilter} onChange={event => setCategoryFilter(event.target.value)}><option>Все категории</option>{categories.map(item => <option key={item}>{item}</option>)}</select><ChevronDown size={16} /></label>
              {(search || statusFilter !== 'Все статусы' || categoryFilter !== 'Все категории') && <button className="button ghost reset-button" onClick={resetFilters}><FilterX size={17} />Сбросить</button>}
            </div>
            <div className="results-caption">Найдено: <strong>{filtered.length}</strong></div>
            {filtered.length ? <div className="request-list">{filtered.map(item => <article className="request-row" key={item.id}>
              <div className="request-main"><div className="request-meta"><span className="request-number">#{item.id}</span><StatusBadge status={item.status} /><span className={`priority priority-${item.priority}`}>{item.priority} приоритет</span></div>
                <button className="request-title" onClick={() => openRequest(item.id)}>{item.title}</button>
                <div className="request-details"><span><Building2 size={15} />{item.category}</span><span><UserRound size={15} />{item.applicant}</span><span><CalendarDays size={15} />{item.created}</span></div></div>
              <div className="request-assignee"><span>Исполнитель</span><strong>{item.assignee}</strong></div>
              <button className="button secondary open-button" onClick={() => openRequest(item.id)}>Открыть<ArrowRight size={16} /></button>
            </article>)}</div> : <div className="empty-state"><div className="empty-icon"><Search size={28} /></div><h2>Ничего не найдено</h2><p>По заданным условиям заявок нет.<br />Измените запрос или сбросьте фильтры.</p><button className="button primary" onClick={resetFilters}><FilterX size={18} />Сбросить фильтры</button></div>}
          </section>
        </>}

        {(view === 'create' || view === 'edit') && <>
          <button className="back-link" onClick={() => view === 'edit' ? setView('details') : goList()}><ArrowLeft size={17} />{view === 'edit' ? 'Вернуться к заявке' : 'Вернуться к списку'}</button>
          <section className="page-heading form-heading"><div><h1>{view === 'create' ? 'Новая заявка' : `Редактирование заявки #${selectedId}`}</h1><p>{view === 'create' ? 'Опишите проблему — специалист получит обращение сразу после регистрации' : 'Измените необходимые сведения и сохраните результат'}</p></div></section>
          <form className="request-form" onSubmit={submitDraft} noValidate>
            <section className="form-card"><div className="form-section-title"><div><ClipboardList size={20} /></div><span><strong>Основная информация</strong><small>Поля со звёздочкой обязательны для заполнения</small></span></div>
              <div className="form-grid">
                <Field label="Тема обращения" required error={errors.title} className="full"><input value={draft.title} onChange={event => setDraft({ ...draft, title: event.target.value })} placeholder="Например, не работает принтер" aria-invalid={!!errors.title} /></Field>
                <Field label="Категория" required error={errors.category}><div className="select-wrap form-select"><select value={draft.category} onChange={event => setDraft({ ...draft, category: event.target.value })} aria-invalid={!!errors.category}><option value="">Выберите категорию</option>{categories.map(item => <option key={item}>{item}</option>)}</select><ChevronDown size={16} /></div></Field>
                <Field label="Приоритет"><div className="select-wrap form-select"><select value={draft.priority} onChange={event => setDraft({ ...draft, priority: event.target.value as Priority })}><option>Низкий</option><option>Средний</option><option>Высокий</option></select><ChevronDown size={16} /></div></Field>
                <Field label="Заявитель" required error={errors.applicant}><input value={draft.applicant} onChange={event => setDraft({ ...draft, applicant: event.target.value })} placeholder="Фамилия и имя" aria-invalid={!!errors.applicant} /></Field>
                <Field label="Желаемый срок" required error={errors.deadline}><input type="date" value={draft.deadline} onChange={event => setDraft({ ...draft, deadline: event.target.value })} aria-invalid={!!errors.deadline} /></Field>
                {view === 'edit' && <><Field label="Статус"><div className="select-wrap form-select"><select value={draft.status} onChange={event => setDraft({ ...draft, status: event.target.value as Status })}>{statuses.map(item => <option key={item}>{item}</option>)}</select><ChevronDown size={16} /></div></Field><Field label="Исполнитель"><div className="select-wrap form-select"><select value={draft.assignee} onChange={event => setDraft({ ...draft, assignee: event.target.value })}>{assignees.map(item => <option key={item}>{item}</option>)}</select><ChevronDown size={16} /></div></Field></>}
                <Field label="Описание проблемы" required error={errors.description} className="full"><textarea value={draft.description} onChange={event => setDraft({ ...draft, description: event.target.value })} placeholder="Что произошло? Где и когда возникла проблема? Укажите важные детали." rows={6} aria-invalid={!!errors.description} /><span className="character-count">{draft.description.length} символов</span></Field>
              </div>
            </section>
            <div className="form-actions"><button type="button" className="button secondary" onClick={() => view === 'edit' ? setView('details') : goList()}>Отмена</button><button type="submit" className="button primary"><Check size={18} />{view === 'create' ? 'Создать заявку' : 'Сохранить изменения'}</button></div>
          </form>
        </>}

        {view === 'details' && selected && <>
          <button className="back-link" onClick={goList}><ArrowLeft size={17} />Вернуться к списку</button>
          <section className="page-heading detail-heading"><div><div className="detail-label">{number(selected.id)}<StatusBadge status={selected.status} /></div><h1>{selected.title}</h1><p>Создана {selected.created}</p></div><div className="heading-actions"><button className="button secondary" onClick={goEdit}><Pencil size={17} />Редактировать</button><button className="button danger-ghost" onClick={() => setDeleteOpen(true)}><Trash2 size={17} />Удалить</button></div></section>
          <div className="details-layout"><div className="details-main">
            <section className="detail-card"><div className="card-heading"><h2>Описание</h2></div><p className="description-text">{selected.description}</p><div className="attachment"><Paperclip size={16} /><span>Материалы не прикреплены</span></div></section>
            <section className="detail-card"><div className="card-heading"><h2>Комментарии</h2><span className="small-count">{selected.comments.length}</span></div>
              {selected.comments.length ? <div className="comments-list">{selected.comments.map((item, index) => <div className="comment" key={`${item.time}-${index}`}><div className="avatar small">{item.author.split(' ').map(part => part[0]).join('').slice(0, 2)}</div><div><div className="comment-meta"><strong>{item.author}</strong><span>{item.time}</span></div><p>{item.text}</p></div></div>)}</div> : <p className="muted-block">Комментариев пока нет. Добавьте первый, чтобы уточнить детали.</p>}
              <form className="comment-form" onSubmit={addComment}><label htmlFor="comment">Добавить комментарий</label><textarea id="comment" value={comment} onChange={event => { setComment(event.target.value); setCommentError('') }} placeholder="Введите сообщение участникам заявки" rows={3} aria-invalid={!!commentError} />{commentError && <span className="field-error">{commentError}</span>}<div><button className="button primary" type="submit"><Send size={16} />Отправить</button></div></form>
            </section>
          </div><aside className="details-side">
            <section className="detail-card info-card"><div className="card-heading"><h2>Сведения</h2></div><InfoRow icon={<Building2 size={17} />} label="Категория" value={selected.category} /><InfoRow icon={<UserRound size={17} />} label="Заявитель" value={selected.applicant} /><InfoRow icon={<UsersRound size={17} />} label="Исполнитель" value={selected.assignee} /><InfoRow icon={<CalendarDays size={17} />} label="Срок выполнения" value={selected.deadline} /><InfoRow icon={<BellRing size={17} />} label="Приоритет" value={selected.priority} /></section>
            {selected.status === 'Новая' && <button className="button primary wide" onClick={takeInWork}><LoaderCircle size={18} />Взять в работу</button>}
            <section className="detail-card history-card"><div className="card-heading"><h2>История</h2></div><div className="timeline">{selected.history.slice().reverse().map((item, index) => { const [date, action] = item.split(' — '); return <div className="timeline-item" key={`${item}-${index}`}><span className="timeline-dot" /><div><strong>{action}</strong><span>{date}</span></div></div> })}</div></section>
          </aside></div>
        </>}
      </div>
    </main>

    {deleteOpen && selected && <Modal onClose={() => setDeleteOpen(false)} className="delete-modal"><div className="warning-icon"><AlertTriangle size={26} /></div><h2>Удалить заявку #{selected.id}?</h2><p>Будут безвозвратно удалены описание, комментарии и история изменений. Это действие нельзя отменить.</p><div className="modal-request-title">{selected.title}</div><div className="modal-actions"><button className="button secondary" onClick={() => setDeleteOpen(false)}>Отмена</button><button className="button danger" onClick={deleteRequest}><Trash2 size={17} />Удалить заявку</button></div></Modal>}
    {helpOpen && <Modal onClose={() => setHelpOpen(false)} className="help-modal"><div className="help-icon"><CircleHelp size={25} /></div><h2>Как работать с прототипом</h2><div className="help-steps"><p><strong>1.</strong> Найдите заявку по номеру или теме.</p><p><strong>2.</strong> Откройте карточку, чтобы увидеть историю и комментарии.</p><p><strong>3.</strong> Создайте обращение или измените существующее.</p></div><p className="help-note">Это интерактивный учебный прототип. Данные сохраняются в localStorage текущего браузера и не отправляются на сервер.</p><button className="button primary wide" onClick={() => setHelpOpen(false)}>Понятно</button></Modal>}
    {toast && <div className="toast" role="status"><CheckCircle2 size={19} />{toast}<button onClick={() => setToast('')} aria-label="Закрыть уведомление"><X size={16} /></button></div>}
  </div>
}

function LoginScreen({ login, password, showPassword, error, loading, setLogin, setPassword, setShowPassword, onSubmit }: {
  login: string; password: string; showPassword: boolean; error: string; loading: boolean
  setLogin: (value: string) => void; setPassword: (value: string) => void; setShowPassword: (value: boolean) => void; onSubmit: (event: FormEvent) => void
}) {
  return <main className="login-page"><section className="login-intro"><div className="login-brand"><div className="brand-mark"><ClipboardList size={24} /></div><div><strong>Заявки</strong><span>RequestSystem</span></div></div><div className="intro-copy"><span className="intro-label"><ShieldCheck size={16} />Единая служба поддержки</span><h1>Каждая заявка<br />под контролем.</h1><p>Регистрируйте обращения, назначайте исполнителей и отслеживайте результат в одном месте.</p><div className="intro-features"><span><CheckCircle2 size={18} />Прозрачная история работы</span><span><CheckCircle2 size={18} />Понятные статусы и сроки</span><span><CheckCircle2 size={18} />Быстрое взаимодействие</span></div></div><div className="intro-footer">Учебный проект · Гатин Тимофей · еозИСИП-308</div></section>
    <section className="login-form-side"><div className="login-box"><div className="mobile-login-brand"><ClipboardList size={24} /><strong>RequestSystem</strong></div><span className="login-kicker">Добро пожаловать</span><h2>Вход в систему</h2><p>Используйте демонстрационную учётную запись</p><form onSubmit={onSubmit} noValidate><label className="login-field"><span>Логин</span><div className="input-with-icon"><UserRound size={18} /><input autoComplete="username" value={login} onChange={event => setLogin(event.target.value)} placeholder="Введите логин" /></div></label><label className="login-field"><span>Пароль</span><div className="input-with-icon"><ShieldCheck size={18} /><input type={showPassword ? 'text' : 'password'} autoComplete="current-password" value={password} onChange={event => setPassword(event.target.value)} placeholder="Введите пароль" /><button type="button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? 'Скрыть пароль' : 'Показать пароль'}>{showPassword ? <EyeOff size={18} /> : <Eye size={18} />}</button></div></label>{error && <div className="login-error" role="alert"><AlertTriangle size={17} />{error}</div>}<button className="button primary login-button" type="submit" disabled={loading}>{loading ? <LoaderCircle size={18} className="spin" /> : <ArrowRight size={18} />}{loading ? 'Выполняется вход…' : 'Войти в систему'}</button></form><div className="demo-credentials"><span>Данные для входа</span><button type="button" onClick={() => { setLogin('operator'); setPassword('12345') }}><code>operator</code><code>12345</code><span>Заполнить</span></button></div></div><div className="login-copyright">Интерактивный прототип · 2026</div></section></main>
}

function StatusBadge({ status }: { status: Status }) { return <span className={`status status-${status}`}>{status === 'Новая' ? <BellRing size={13} /> : status === 'В работе' ? <Clock3 size={13} /> : status === 'Ожидает' ? <LoaderCircle size={13} /> : <CheckCircle2 size={13} />}{status}</span> }
function Field({ label, required, error, className = '', children }: { label: string; required?: boolean; error?: string; className?: string; children: React.ReactNode }) { return <label className={`form-field ${className}`}><span className="field-label">{label}{required && <b> *</b>}</span>{children}{error && <span className="field-error">{error}</span>}</label> }
function InfoRow({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) { return <div className="info-row"><span>{icon}{label}</span><strong>{value}</strong></div> }
function Modal({ onClose, className, children }: { onClose: () => void; className: string; children: React.ReactNode }) { return <div className="modal-layer" role="presentation" onMouseDown={event => { if (event.target === event.currentTarget) onClose() }}><section className={`modal ${className}`} role="dialog" aria-modal="true"><button className="modal-close icon-button" onClick={onClose} aria-label="Закрыть окно"><X size={20} /></button>{children}</section></div> }
