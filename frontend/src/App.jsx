import { useMemo, useState } from 'react'
import './App.css'

const API_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000/api/describe/'

const SUPPORTED_EXT = new Set(['.jpg', '.jpeg', '.png', '.gif', '.webp'])
const MAX_MB = 5

function extOf(name) {
  const lower = (name || '').toLowerCase()
  const idx = lower.lastIndexOf('.')
  return idx >= 0 ? lower.slice(idx) : ''
}

function formatUnknown(obj) {
  if (obj == null) return ''
  if (typeof obj === 'string') return obj
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}

function App() {
  const [file, setFile] = useState(null)
  const [hint, setHint] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const fileMeta = useMemo(() => {
    if (!file) return { ok: false, msg: 'Файл не выбран' }
    const suffix = extOf(file.name)
    if (!SUPPORTED_EXT.has(suffix)) return { ok: false, msg: 'Неподдерживаемый формат' }
    const sizeMb = file.size / (1024 * 1024)
    if (sizeMb > MAX_MB) return { ok: false, msg: `Слишком большой файл (${sizeMb.toFixed(1)} MB)` }
    return { ok: true, msg: `Готово: ${Math.round(sizeMb * 10) / 10} MB` }
  }, [file])

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setResult(null)

    if (!file) {
      setError('Выберите изображение')
      return
    }
    if (!fileMeta.ok) {
      setError(fileMeta.msg)
      return
    }

    setBusy(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      if (hint.trim()) fd.append('hint', hint.trim())

      const resp = await fetch(API_URL, {
        method: 'POST',
        body: fd,
      })

      const data = await resp.json().catch(() => ({}))
      if (!resp.ok) {
        setError(data?.error ? String(data.error) : `Ошибка HTTP ${resp.status}`)
        return
      }
      setResult(data)
    } catch (err) {
      setError(err?.message ? String(err.message) : String(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="header">
        <h1>Photo Description Generator</h1>
        <p className="sub">
          Загружайте фото, получайте структурированное описание в JSON для маркетплейсов и фотостоков.
        </p>
      </header>

      <main className="grid">
        <section className="card">
          <form onSubmit={onSubmit}>
            <label className="label">
              Фото
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.gif,.webp"
                onChange={(e) => {
                  const f = e.target.files && e.target.files[0] ? e.target.files[0] : null
                  setFile(f)
                }}
              />
            </label>

            <div className="meta">{file ? fileMeta.msg : 'Выберите изображение (до 5 MB).'}</div>

            <label className="label">
              Подсказка (опционально)
              <input
                type="text"
                placeholder="например: товар из кожи / для кухни / бренд и т.д."
                value={hint}
                onChange={(e) => setHint(e.target.value)}
              />
            </label>

            <button className="btn" type="submit" disabled={busy}>
              {busy ? 'Анализирую…' : 'Сгенерировать описание'}
            </button>

            {error ? <div className="error">Ошибка: {error}</div> : null}
          </form>
        </section>

        <section className="card result">
          {!result ? (
            <div className="placeholder">
              Результат появится здесь после отправки изображения.
            </div>
          ) : (
            <>
              <div className="result-row">
                <div className="k">title</div>
                <div className="v">{formatUnknown(result.title ?? result?.raw)}</div>
              </div>
              {result.short_description ? (
                <div className="result-row">
                  <div className="k">short_description</div>
                  <div className="v">{result.short_description}</div>
                </div>
              ) : null}
              {result.full_description ? (
                <div className="result-row">
                  <div className="k">full_description</div>
                  <div className="v">{result.full_description}</div>
                </div>
              ) : null}
              {result.tags ? (
                <div className="result-row">
                  <div className="k">tags</div>
                  <div className="v">{result.tags}</div>
                </div>
              ) : null}
              {result.category ? (
                <div className="result-row">
                  <div className="k">category</div>
                  <div className="v">{result.category}</div>
                </div>
              ) : null}

              {result._usage ? (
                <div className="usage">
                  usage: input_tokens={result._usage.input_tokens}, output_tokens={result._usage.output_tokens}
                </div>
              ) : null}

              {result.raw ? (
                <details className="raw">
                  <summary>Сырой ответ</summary>
                  <pre>{formatUnknown(result.raw)}</pre>
                </details>
              ) : null}

              <details className="raw">
                <summary>Полный JSON</summary>
                <pre>{formatUnknown(result)}</pre>
              </details>
            </>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
