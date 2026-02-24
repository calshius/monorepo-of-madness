import { render, screen, cleanup } from '@testing-library/svelte';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import Page from './+page.svelte';

// Mock fetch globally
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

describe('+page.svelte', () => {
	beforeEach(() => {
		mockFetch.mockReset();
	});

	afterEach(() => {
		cleanup();
	});

	it('renders the heading', async () => {
		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => []
		});

		render(Page);
		expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Items');
	});

	it('shows empty message when no items', async () => {
		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => []
		});

		render(Page);

		// Wait for fetch to resolve
		await vi.waitFor(() => {
			expect(screen.getByTestId('empty-message')).toHaveTextContent('No items yet.');
		});
	});

	it('renders the add item form', async () => {
		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => []
		});

		render(Page);
		expect(screen.getByTestId('name-input')).toBeInTheDocument();
		expect(screen.getByTestId('desc-input')).toBeInTheDocument();
		expect(screen.getByRole('button', { name: 'Add Item' })).toBeInTheDocument();
	});

	it('displays items when API returns data', async () => {
		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => [
				{ id: 1, name: 'Widget', description: 'A fine widget' },
				{ id: 2, name: 'Gadget', description: '' }
			]
		});

		render(Page);

		await vi.waitFor(() => {
			const items = screen.getAllByTestId('item');
			expect(items).toHaveLength(2);
			expect(items[0]).toHaveTextContent('Widget');
			expect(items[1]).toHaveTextContent('Gadget');
		});
	});

	it('shows error when fetch fails', async () => {
		mockFetch.mockRejectedValueOnce(new Error('Network error'));

		render(Page);

		await vi.waitFor(() => {
			expect(screen.getByRole('alert')).toHaveTextContent('Failed to load items');
		});
	});
});
