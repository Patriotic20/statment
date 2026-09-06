import { useState, type InputHTMLAttributes, type SelectHTMLAttributes, type ReactNode } from 'react'
import { Eye, EyeOff } from 'lucide-react'

const base =
  'w-full rounded-input border border-border bg-surface px-3 py-2 text-sm text-ink placeholder:text-tertiary outline-none transition focus:border-accent focus:ring-2 focus:ring-accent-soft'

export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-xs font-medium text-muted">{label}</span>
      {children}
    </label>
  )
}

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={`${base} ${props.className ?? ''}`} />
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  options: { value: string; label: string }[]
}

export function Select({ options, className, ...rest }: SelectProps) {
  return (
    <select {...rest} className={`${base} ${className ?? ''}`}>
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  )
}

/**
 * Поле пароля с переключателем видимости.
 *
 * Показанный пароль можно проверить глазами и скопировать: из полей
 * type="password" браузеры копировать не дают.
 */
export function PasswordInput({ className, ...rest }: InputHTMLAttributes<HTMLInputElement>) {
  const [visible, setVisible] = useState(false)
  return (
    <div className="relative">
      <input
        {...rest}
        type={visible ? 'text' : 'password'}
        className={`${base} pr-11 ${className ?? ''}`}
      />
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        // Не даём label перехватить клик и увести фокус в поле.
        onMouseDown={(e) => e.preventDefault()}
        aria-label={visible ? 'Parolni yashirish' : "Parolni ko'rsatish"}
        title={visible ? 'Parolni yashirish' : "Parolni ko'rsatish"}
        className="absolute inset-y-0 right-0 grid w-11 place-items-center text-tertiary transition hover:text-muted"
      >
        {visible ? <EyeOff size={17} /> : <Eye size={17} />}
      </button>
    </div>
  )
}
