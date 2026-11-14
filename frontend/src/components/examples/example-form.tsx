import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import type { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAppDispatch } from '@/hooks/use-app-dispatch'
import { useAppSelector } from '@/hooks/use-app-selector'
import { setWorkspaceName } from '@/redux/slices/app-slice'
import { exampleFormSchema } from '@/schemas/example-form'

export function ExampleForm() {
  const dispatch = useAppDispatch()
  const workspaceName = useAppSelector((state) => state.app.workspaceName)
  const [saved, setSaved] = useState(false)
  const { register, handleSubmit, formState: { errors } } = useForm<z.infer<typeof exampleFormSchema>>({
    resolver: zodResolver(exampleFormSchema),
    defaultValues: { workspaceName },
  })

  return (
    <form onSubmit={handleSubmit((values) => { dispatch(setWorkspaceName(values.workspaceName)); setSaved(true) })} className="space-y-5">
      <div className="space-y-2">
        <Label htmlFor="workspace-name">Nama workspace</Label>
        <Input id="workspace-name" {...register('workspaceName', { onChange: () => setSaved(false) })} aria-invalid={!!errors.workspaceName} aria-describedby={errors.workspaceName ? 'workspace-error' : 'workspace-help'} />
        {errors.workspaceName
          ? <p id="workspace-error" role="alert" className="text-sm text-destructive">{errors.workspaceName.message}</p>
          : <p id="workspace-help" className="text-sm text-muted-foreground">Contoh form lokal. Tidak mengirim data ke database.</p>}
      </div>
      <div className="flex flex-wrap items-center gap-4">
        <Button type="submit">Simpan nama</Button>
        <span role="status" className="text-sm text-primary">{saved ? 'Nama workspace disimpan untuk sesi ini.' : ''}</span>
      </div>
    </form>
  )
}
