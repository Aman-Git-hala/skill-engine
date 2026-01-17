import pickle
import os
import numpy as np
from analyzer.graphcodebert import get_embedding

# Ensure the folder exists
if not os.path.exists("reference_embeddings"):
    os.makedirs("reference_embeddings")

print("⏳ Generating Professional Reference Embeddings (The Ultimate List)...")

# ==========================================
#  PROFESSIONAL CODE SNIPPETS (Gold Standard)
# ==========================================

# 1. PYTHON (General)
python_code = """
class DataProcessor:
    def __init__(self, data: list[dict]):
        self.data = data
        self._cache = {}

    @property
    def processed_data(self):
        if 'clean' not in self._cache:
            self._cache['clean'] = [d for d in self.data if d.get('active')]
        return self._cache['clean']
"""

# 2. DJANGO (Backend Web)
django_code = """
from django.db import models
from django.views.generic import ListView

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    def is_in_stock(self):
        return self.stock > 0

class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        return Product.objects.filter(stock__gt=0).order_by('-price')
"""

# 3. PANDAS (Data Science)
pandas_code = """
import pandas as pd
import numpy as np

def analyze_sales(file_path):
    df = pd.read_csv(file_path)
    # Group by category and calculate aggregate metrics
    summary = df.groupby('category').agg({
        'revenue': ['sum', 'mean'],
        'quantity': 'sum',
        'customer_id': pd.Series.nunique
    })
    
    # Calculate rolling average
    df['rolling_avg'] = df['revenue'].rolling(window=7).mean()
    
    # Filter high-value transactions
    high_value = df[df['revenue'] > df['revenue'].quantile(0.95)]
    return summary, high_value
"""

# 4. FLUTTER (Mobile)
flutter_code = """
import 'package:flutter/material.dart';

class UserProfile extends StatelessWidget {
  final User user;

  const UserProfile({Key? key, required this.user}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(user.name)),
      body: ListView.builder(
        itemCount: user.posts.length,
        itemBuilder: (context, index) {
          return Card(
            margin: EdgeInsets.all(8.0),
            child: ListTile(
              leading: CircleAvatar(backgroundImage: NetworkImage(user.avatar)),
              title: Text(user.posts[index].title),
              subtitle: Text(user.posts[index].date),
              trailing: Icon(Icons.arrow_forward_ios),
            ),
          );
        },
      ),
    );
  }
}
"""

# 5. DOCKER (DevOps)
docker_code = """
# Multi-stage build for optimized image size
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""

# 6. SQL (Database)
sql_code = """
SELECT 
    u.id, 
    u.username, 
    COUNT(o.id) as total_orders,
    SUM(o.amount) as total_spent
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.created_at >= '2023-01-01'
GROUP BY u.id, u.username
HAVING COUNT(o.id) > 5
ORDER BY total_spent DESC;
"""

# 7. C (Systems)
c_code = """
struct task_struct *find_task_by_vpid(pid_t vpid) {
    struct task_struct *task;
    rcu_read_lock();
    task = pid_task(find_vpid(vpid), PIDTYPE_PID);
    if (task) get_task_struct(task);
    rcu_read_unlock();
    return task;
}
"""

# 8. C++ (Competitive / Systems)
cpp_code = """
#include <vector>
#include <algorithm>
#include <iostream>

template <typename T>
class Matrix {
    std::vector<std::vector<T>> data;
public:
    Matrix(int rows, int cols) : data(rows, std::vector<T>(cols)) {}
    
    void multiply(const Matrix& other) {
        // Simple O(N^3) multiplication logic
        for(int i=0; i<rows; i++) {
            for(int j=0; j<cols; j++) {
                // ... implementation ...
            }
        }
    }
};
"""

# 9. JAVASCRIPT / REACT (Web)
js_code = """
import React, { useState, useEffect } from 'react';

export const Dashboard = () => {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    fetch('/api/data')
      .then(res => res.json())
      .then(json => setData(json.filter(item => item.isActive)));
  }, []);

  return (
    <div className="grid">
      {data.map(item => <Card key={item.id} title={item.name} />)}
    </div>
  );
};
"""

# ==========================================
#  MAPPING & GENERATION
# ==========================================

references = {
    # Core Languages
    "python": python_code,
    "c": c_code,
    "cplusplus": cpp_code,   # Mapped name for C++
    "javascript": js_code,
    "typescript": js_code,   # Similar enough for embeddings
    "java": cpp_code,        # Java/C++ are structurally similar enough
    
    # Frameworks
    "django": django_code,
    "flask": django_code,    # Both are Python backend
    "pandas": pandas_code,
    "numpy": pandas_code,
    
    # Web
    "react": js_code,
    "html": js_code,         # Often mixed
    
    # Mobile
    "flutter": flutter_code,
    
    # DevOps
    "docker": docker_code,
    
    # Database
    "sql": sql_code
}

count = 0
for skill, code in references.items():
    print(f"   ... Processing {skill} ...")
    emb = get_embedding(code)
    
    # Save to file
    with open(f"reference_embeddings/{skill}.pkl", "wb") as f:
        pickle.dump(emb, f)
    count += 1

print(f" Done! Generated {count} professional references.")