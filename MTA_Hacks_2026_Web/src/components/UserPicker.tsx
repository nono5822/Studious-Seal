import { useState, useEffect } from 'react'
import type { ApiState } from '../services/api'
import { fetchUsers, fetchDashboard, setBaseURL, setUsername, loadMockDashboard } from '../services/api'

interface UserPickerProps {
  api: ApiState
  setApi: (patch: Partial<ApiState>) => void
  onClose: () => void
}

export function UserPicker({ api, setApi, onClose }: UserPickerProps) {
  const [baseURLInput, setBaseURLInput] = useState(api.baseURLString)
  const [usernameInput, setUsernameInput] = useState(api.username ?? '')
  const [loadingUsers, setLoadingUsers] = useState(false)

  useEffect(() => {
    setBaseURLInput(api.baseURLString)
    setUsernameInput(api.username ?? '')
  }, [api.baseURLString, api.username])

  const handleSaveURL = () => {
    const next = setBaseURL(baseURLInput)
    setApi({ baseURLString: next })
  }

  const handleLoadUsers = async () => {
    setLoadingUsers(true)
    const { users, error } = await fetchUsers(api)
    setApi({ users, error })
    setLoadingUsers(false)
  }

  const handleUseUser = (user: string) => {
    const nextUser = setUsername(user)
    setApi({ username: nextUser })
    setUsernameInput(user)
    fetchDashboard({ ...api, username: nextUser }).then(({ dashboard, error }) => {
      setApi({ dashboard, error })
    })
    onClose()
  }

  const handleUseThisUsername = async () => {
    const name = usernameInput.trim() || null
    const nextUser = setUsername(name)
    setApi({ username: nextUser })
    setApi({ isLoading: true, error: null })
    const { dashboard, error } = await fetchDashboard({ ...api, username: nextUser })
    setApi({ dashboard, error, isLoading: false })
    onClose()
  }

  const handleMockData = () => {
    setApi({ dashboard: loadMockDashboard(), error: null })
    onClose()
  }

  return (
    <div className="user-picker-overlay" onClick={onClose}>
      <div className="user-picker" onClick={(e) => e.stopPropagation()}>
        <div className="user-picker-header">
          <h2>Server & User</h2>
          <button type="button" className="btn-text" onClick={onClose}>Done</button>
        </div>
        <div className="user-picker-body">
          <section>
            <h3>Server</h3>
            <input
              type="url"
              value={baseURLInput}
              onChange={(e) => setBaseURLInput(e.target.value)}
              placeholder="http://localhost:5000/"
            />
            <button type="button" className="btn-primary" onClick={handleSaveURL}>Save URL</button>
            <p className="hint">e.g. http://localhost:5000/ or your ngrok URL.</p>
          </section>
          <section>
            <h3>User</h3>
            <input
              type="text"
              value={usernameInput}
              onChange={(e) => setUsernameInput(e.target.value)}
              placeholder="Username"
            />
            <button type="button" className="btn-primary" onClick={handleLoadUsers} disabled={loadingUsers}>
              {loadingUsers ? 'Loading…' : 'Load user list'}
            </button>
            {api.users.length > 0 && (
              <ul className="user-list">
                {api.users.map((user) => (
                  <li key={user}>
                    <button
                      type="button"
                      className="user-item"
                      onClick={() => handleUseUser(user)}
                    >
                      {user}
                      {api.username === user && <span className="check">✓</span>}
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <p className="hint">Type a username or pick one from the list.</p>
          </section>
          <section>
            <button type="button" className="btn-primary" onClick={handleUseThisUsername} disabled={!usernameInput.trim()}>
              Use this username
            </button>
          </section>
          <section>
            <button type="button" className="btn-secondary" onClick={handleMockData}>
              Use mock data
            </button>
          </section>
        </div>
      </div>
    </div>
  )
}
