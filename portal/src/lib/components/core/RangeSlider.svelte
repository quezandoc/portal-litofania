<script lang="ts">
  let {
    title,
    id,
    min,
    max,
    step = 0.1,
    value = $bindable(),
  } = $props<{
    title: string;
    id: string;
    min: number;
    max: number;
    step?: number;
    value: number;
  }>();

  const progress = $derived(((value - min) / (max - min)) * 100);
</script>

<div class="range-field">
  <label class="range-label" for={id}>
    {title}
    <span class="range-value">{value}</span>
  </label>

  <input
    {id}
    type="range"
    {min}
    {max}
    {step}
    bind:value
    class="range"
    style="--range-progress: {progress}%"
  />
</div>

<style>
  /* === RANGE INPUT === */

  .range-field {
    margin-block: 1.5rem;
  }

  .range-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    font-size: 1rem;
    font-weight: 500;
    color: var(--text-primary);
  }

  .range-value {
    font-size: 0.875rem;
    color: var(--text-secondary);
    background-color: var(--bg-secondary);
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
  }

  /* Base */
  .range {
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 0.5rem;
    border-radius: 9999px;
    background: linear-gradient(
      to right,
      var(--color-primary-500) 0%,
      var(--color-primary-300) var(--range-progress, 50%),
      var(--bg-secondary) var(--range-progress, 50%),
      var(--bg-secondary) 100%
    );
    cursor: pointer;
    transition: background 0.2s ease;
  }

  /* Progreso Firefox */
  .range::-moz-range-progress {
    height: 0.5rem;
    border-radius: 9999px;
    background: linear-gradient(
      to right,
      var(--color-primary-500),
      var(--color-primary-300)
    );
  }

  /* WebKit thumb */
  .range::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 1.25rem;
    height: 1.25rem;
    border-radius: 50%;
    background-color: var(--color-primary-500);
    border: 3px solid var(--bg-primary);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    transition:
      transform 0.15s ease,
      box-shadow 0.15s ease;
  }

  .range::-webkit-slider-thumb:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
  }

  /* Firefox thumb */
  .range::-moz-range-thumb {
    width: 1.25rem;
    height: 1.25rem;
    border-radius: 50%;
    background-color: var(--color-primary-500);
    border: 3px solid var(--bg-primary);
    cursor: pointer;
  }

  /* Track Firefox */
  .range::-moz-range-track {
    height: 0.5rem;
    border-radius: 9999px;
    background-color: var(--bg-secondary);
  }
</style>
