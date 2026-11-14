import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

const appSlice = createSlice({
  name: 'app',
  initialState: { workspaceName: 'Workspace pengembangan' },
  reducers: {
    setWorkspaceName(state, action: PayloadAction<string>) {
      state.workspaceName = action.payload
    },
  },
})

export const { setWorkspaceName } = appSlice.actions
export default appSlice.reducer
