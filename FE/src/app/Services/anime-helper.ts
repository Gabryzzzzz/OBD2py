let anime: any;

export async function getAnime() {
  if (!anime) {
    anime = (await import('animejs') as any).default;
  }
  return anime;
}
