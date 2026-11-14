import { z } from 'zod'

export const exampleFormSchema = z.object({
  workspaceName: z.string().trim().min(2, 'Gunakan minimal 2 karakter.').max(80, 'Maksimal 80 karakter.'),
})
