import * as React from "react"
const Alert = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement> & {variant?: 'default' | 'destructive'}>(({ className, variant = 'default', ...props }, ref) => {
  const variants = {default: "bg-background text-foreground border-border", destructive: "border-red-500 bg-red-50 text-red-900"}
  return (<div ref={ref} role="alert" className={'relative w-full rounded-lg border p-4 ' + variants[variant] + ' ' + (className || '')} {...props} />)
})
Alert.displayName = "Alert"
const AlertDescription = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(({ className, ...props }, ref) => (<div ref={ref} className={'text-sm ' + (className || '')} {...props} />))
AlertDescription.displayName = "AlertDescription"
export { Alert, AlertDescription }
