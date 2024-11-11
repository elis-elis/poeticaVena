/** 
The login form captures the user's email and password.
It sends a POST request to your backend's /auth/login endpoint.
If successful, it stores the JWT token in localStorage and redirects the user to the homepage.
*/

import { useState } from 'react';
import api from '@/utils/api'; // The axios instance is already set up
import { useRouter } from 'next/router';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const router = useRouter();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await api.post('/auth/login', {
                email,
                password,
            });
            const token = response.data.access_token;

            // Stores the JWT token in localStorage
            localStorage.setItem('token', token);

            console.log('Volia! Login successful, token stored:', token);
            // Redirect poet to homepage or another protected route
            router.push('/');
            } catch (error) {
            console.error('eeeee! Login failed:', error.response?.data || error.message);
            alert('oops! Login failed. Please check your credentials.');
            }
        };

    return (
        <div>
            <h1>login, gently, but confidently</h1>
            <form onSubmit={handleLogin}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button type="submit">nigol</button>
            </form>
        </div>
    );
}
