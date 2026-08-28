import { BookOpen, Bus, Clapperboard, HeartPulse, Home, MoreHorizontal, ReceiptText, ShoppingBag, Utensils } from 'lucide-react';

export const categories = [
  { name: 'Food', icon: Utensils, color: '#ef6c62', soft: '#fff0ee' },
  { name: 'Transport', icon: Bus, color: '#5d8fe8', soft: '#edf3ff' },
  { name: 'Housing', icon: Home, color: '#8c6dd7', soft: '#f3effb' },
  { name: 'Utilities', icon: ReceiptText, color: '#ff9f43', soft: '#fff4e7' },
  { name: 'Shopping', icon: ShoppingBag, color: '#e98bb1', soft: '#fff0f6' },
  { name: 'Health', icon: HeartPulse, color: '#48aa84', soft: '#eaf8f1' },
  { name: 'Entertainment', icon: Clapperboard, color: '#6eb7c5', soft: '#ecf7f9' },
  { name: 'Education', icon: BookOpen, color: '#9aac55', soft: '#f4f7e8' },
  { name: 'Other', icon: MoreHorizontal, color: '#849089', soft: '#f1f3f2' }
];

export const categoryMap = new Map(categories.map(category => [category.name, category]));
