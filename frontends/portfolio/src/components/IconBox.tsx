import Icon, { type IconName } from './Icon'

export default function IconBox({ name }: { name: IconName }) {
  return (
    <div className="w-10 h-10 rounded-md border border-border flex items-center justify-center text-secondary shrink-0">
      <Icon name={name} />
    </div>
  )
}
