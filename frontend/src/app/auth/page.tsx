"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/Button";
import { Input } from "@/components/Input";
import { Card } from "@/components/Card";
import toast from "react-hot-toast";

export default function AuthPage() {
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Check if already authenticated
    const checkAuth = async () => {
      const response = await fetch('/api/auth/check');
      if (response.ok) {
        router.push('/');
      }
    };
    checkAuth();
  }, [router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password }),
      });

      if (response.ok) {
        toast.success('Authentication successful!');
        router.push('/');
        router.refresh();
      } else {
        toast.error('Incorrect password. Please try again.');
        setPassword("");
      }
    } catch (error) {
      toast.error('Authentication failed. Please try again.');
      setPassword("");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex items-center justify-center min-h-screen bg-gray-50">
      <Card className="max-w-md w-full mx-4">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            DocAssist AI
          </h1>
          <p className="text-gray-600">Please enter the password to continue</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            type="password"
            label="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter password"
            disabled={loading}
            autoFocus
            required
          />
          <Button
            type="submit"
            isLoading={loading}
            disabled={!password.trim()}
            className="w-full"
          >
            Access Application
          </Button>
        </form>
      </Card>
    </main>
  );
}

