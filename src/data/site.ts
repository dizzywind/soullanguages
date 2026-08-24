import home from './content/home.json';
import repentance from './content/repentance-chant.json';
import tara from './content/green-tara-mantra.json';
import bodhicitta from './content/bodhicitta.json';
import heartSutra from './content/heart-sutra.json';
import ksitigarbha from './content/ksitigarbha.json';
import emptiness from './content/about-emptiness.json';
import mindBuddha from './content/mind-buddha.json';

export type Locale = 'zh' | 'en';

export const site = {
  name: { zh: '靈語堂', en: 'Soul Languages' },
  youtubeUrl: home.youtube_url as string,
  contactUrl: home.contact_url as string,
};

export type Block =
  | { t: 'pair'; hanzi: string; pinyin: string }
  | { t: 'line'; text: string }
  | { t: 'heading' | 'para' | 'bullet' | 'mantra' | 'translit' | 'p'; text: string };

interface VariantData {
  title_pinyin?: string;
  blocks: Block[];
}

export interface Sutra {
  slug: string;
  order: number;
  titles: { zh: string; en: string };
  image?: string;
  image_alt?: string;
  pinyin_title?: boolean;
  variants: Record<string, VariantData | Block[]>;
}

export const sutras: Sutra[] = [
  repentance,
  tara,
  bodhicitta,
  heartSutra,
  ksitigarbha,
  emptiness,
  mindBuddha,
] as unknown as Sutra[];

export const episodes = home.episodes as Array<{
  num: number;
  yt: string;
  titles: { zh: string; en: string };
}>;

export const downloads = home.downloads as Array<{
  file: string;
  titles: { zh: string; en: string };
}>;

export const ui = {
  nav: {
    home: { zh: '主頁', en: 'Home' },
    sutras: { zh: '經文與分享', en: 'Sutras' },
    downloads: { zh: '下載', en: 'Downloads' },
    contact: { zh: '聯絡我們', en: 'Contact' },
  },
  episodesTitle: { zh: '靈語系列', en: 'Soul Languages Series' },
  subscribe: { zh: '訂閱我們的 YouTube 頻道', en: 'Subscribe on YouTube' },
  downloadPdf: { zh: '下載 PDF', en: 'Download PDF' },
  shareTitle: { zh: '分享', en: 'Sharing' },
  enNote: {
    zh: '',
    en: 'This text is presently available in Chinese only. Pinyin is provided where the original includes it.',
  },
  backToSutras: { zh: '返回經文目錄', en: 'Back to Sutras' },
  notFound: {
    zh: '此頁不存在。請返回主頁。',
    en: 'Page not found. Please return to the homepage.',
  },
} as const;

export function t(key: keyof typeof ui.nav | keyof Omit<typeof ui, 'nav'>, locale: Locale): string {
  const entry = (ui as Record<string, Record<Locale, string>>)[key];
  return entry[locale];
}

const LOCALE_PATH: Record<Locale, string> = { zh: '', en: '/en' };

/** Build a path under the configured base, e.g. /soullanguages/en/sutras */
export function lp(locale: Locale, path = ''): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  return `${base}${LOCALE_PATH[locale]}${path}`;
}

export function sutraVariant(sutra: Sutra, locale: Locale): { key: string; data: VariantData | Block[] } {
  if (locale === 'en' && sutra.variants.en) return { key: 'en', data: sutra.variants.en };
  if (sutra.variants.hant) return { key: 'hant', data: sutra.variants.hant };
  return { key: Object.keys(sutra.variants)[0], data: Object.values(sutra.variants)[0] };
}

export function sutraHasScripts(sutra: Sutra): boolean {
  return Boolean(sutra.variants.hant && sutra.variants.simp);
}
