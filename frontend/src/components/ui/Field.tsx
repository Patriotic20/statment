import type { InputHTMLAttributes, SelectHTMLAttributes, ReactNode } from 'react'

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
